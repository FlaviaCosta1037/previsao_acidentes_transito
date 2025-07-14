import React, { useEffect, useRef, useState } from 'react';
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  PointElement,
} from 'chart.js';
import { MatrixController, MatrixElement } from 'chartjs-chart-matrix';
import { collection, getDocs, addDoc, query, orderBy, where } from 'firebase/firestore';
import { db } from './firebaseConfig';

import 'bootstrap/dist/css/bootstrap.min.css';

Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  PointElement,
  MatrixController,
  MatrixElement
);

function App() {
  const [error, setError] = useState(null);
  const [previsaoProximoDia, setPrevisaoProximoDia] = useState(null);
  const [previsoesHistorico, setPrevisoesHistorico] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [dadosGraficos, setDadosGraficos] = useState(null);

  const refs = {
    ano: useRef(null),
    dia: useRef(null),
    bairros: useRef(null),
    hora: useRef(null),
    tipo: useRef(null),
    natureza: useRef(null),
    veiculos: useRef(null),
    heatmap: useRef(null),
  };

  const instances = {
    ano: useRef(null),
    dia: useRef(null),
    bairros: useRef(null),
    hora: useRef(null),
    tipo: useRef(null),
    natureza: useRef(null),
    veiculos: useRef(null),
    heatmap: useRef(null),
  };

  async function carregarPrevisoesFirestore() {
    try {
      const q = query(collection(db, 'previsoes'), orderBy('data', 'desc'));
      const querySnapshot = await getDocs(q);
      const previsoes = [];
      querySnapshot.forEach((doc) => {
        previsoes.push({ id: doc.id, ...doc.data() });
      });
      setPrevisoesHistorico(previsoes);
    } catch (e) {
      console.error('Erro ao carregar previsões do Firestore:', e);
      setError('Erro ao carregar previsões salvas');
    }
  }

  async function existePrevisaoParaData(dataStr) {
    const previsoesRef = collection(db, 'previsoes');
    const q = query(previsoesRef, where('data', '==', dataStr));
    const snapshot = await getDocs(q);
    return !snapshot.empty;
  }

  function getChartOptions(darkMode) {
    return {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        tooltip: { enabled: true },
        legend: {
          position: 'top',
          labels: {
            color: darkMode ? 'white' : 'black',
          },
        },
      },
      scales: {
        x: {
          ticks: { color: darkMode ? 'white' : 'black' },
          grid: { color: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' },
        },
        y: {
          beginAtZero: true,
          ticks: { color: darkMode ? 'white' : 'black' },
          grid: { color: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' },
        },
      },
    };
  }

  function criarGrafico(ref, instanceRef, tipo, labels, dados, label, cor) {
    if (instanceRef.current) instanceRef.current.destroy();

    instanceRef.current = new Chart(ref.current, {
      type: tipo,
      data: {
        labels,
        datasets: [{
          label,
          data: dados,
          backgroundColor: cor,
          borderColor: cor,
          borderWidth: 1,
        }],
      },
      options: getChartOptions(darkMode),
    });
  }

  function criarHeatmap(ref, instanceRef, data, dias, turnos) {
    if (instanceRef.current) instanceRef.current.destroy();

    const matrixData = data.flatMap((row, y) =>
      row.map((value, x) => ({
        x: turnos[x],
        y: dias[y],
        v: value,
      }))
    );

    instanceRef.current = new Chart(ref.current, {
      type: 'matrix',
      data: {
        datasets: [{
          label: 'Acidentes por Turno e Dia da Semana',
          data: matrixData,
          backgroundColor: (ctx) => {
            const value = ctx.raw.v;
            const max = Math.max(...data.flat());
            const lightness = 90 - 50 * (value / max);
            return `hsl(210, 100%, ${lightness}%)`;
          },
          width: (ctx) => {
            const chartArea = ctx.chart.chartArea;
            if (!chartArea) return 40;
            return Math.min((chartArea.right - chartArea.left) / turnos.length - 4, 80);
          },
          height: (ctx) => {
            const chartArea = ctx.chart.chartArea;
            if (!chartArea) return 40;
            return Math.min((chartArea.bottom - chartArea.top) / dias.length - 4, 40);
          },
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: 20, bottom: 10, left: 10, right: 10 },
        scales: {
          x: {
            type: 'category',
            labels: turnos,
            position: 'top',
            ticks: { font: { size: 12 },               
            maxRotation: 0,
            minRotation: 0,
            autoSkip: false,
            align: 'center',
            padding: 10,
            font: { size: 12 },
            color: darkMode ? 'white' : 'black' },
            grid: { drawOnChartArea: false },
          },
          y: {
            type: 'category',
            labels: dias,
            ticks: { font: { size: 12 }, color: darkMode ? 'white' : 'black' },
            grid: { drawOnChartArea: false },
          },
        },
        plugins: {
          tooltip: {
            callbacks: {
              title: (ctx) => `${ctx[0].raw.y} - ${ctx[0].raw.x}`,
              label: (ctx) => `Acidentes: ${ctx.raw.v}`,
            },
          },
          legend: { display: false },
          title: {
            display: true,
            text: 'Mapa de Calor: Acidentes por Turno e Dia da Semana',
            font: { size: 16, weight: 'bold' },
          },
        },
      },
    });
  }

  useEffect(() => {
    carregarPrevisoesFirestore();
  }, []);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/graficos');
        if (!res.ok) throw new Error('Erro ao buscar gráficos');
        const dados = await res.json();
        setDadosGraficos(dados);

        const resPrevisao = await fetch('http://127.0.0.1:5000/api/previsao');
        if (!resPrevisao.ok) throw new Error('Erro ao buscar previsão');
        const dadosPrevisao = await resPrevisao.json();

        if (dadosPrevisao.error) {
          setError(dadosPrevisao.error);
          return;
        }

        const amanha = new Date();
        amanha.setDate(amanha.getDate() + 1);
        const amanhaStr = amanha.toISOString().split('T')[0];
        setPrevisaoProximoDia(dadosPrevisao.previsao_proximo_dia);

        const existe = await existePrevisaoParaData(amanhaStr);
        if (!existe) {
          await addDoc(collection(db, 'previsoes'), {
            data: amanhaStr,
            previsao: dadosPrevisao.previsao_proximo_dia,
            createdAt: new Date(),
          });
          carregarPrevisoesFirestore();
        }
      } catch (e) {
        console.error('Erro:', e);
        setError(e.message);
      }
    }
    fetchData();
  }, []);

  useEffect(() => {
    if (!dadosGraficos) return;

    criarGrafico(refs.ano, instances.ano, 'bar', dadosGraficos.acidentes_ano.anos, dadosGraficos.acidentes_ano.valores, 'Acidentes por Ano', 'rgba(54, 162, 235, 0.8)');
    criarGrafico(refs.dia, instances.dia, 'bar', dadosGraficos.acidentes_dia.dias, dadosGraficos.acidentes_dia.valores, 'Acidentes por Dia da Semana', 'rgba(75, 192, 192, 0.8)');
    criarGrafico(refs.bairros, instances.bairros, 'bar', dadosGraficos.top_bairros.bairros, dadosGraficos.top_bairros.valores, 'Top 10 Bairros', 'rgba(255, 159, 64, 0.8)');
    criarGrafico(refs.hora, instances.hora, 'bar', dadosGraficos.hora_dia.horas.map(h => `${h}h`), dadosGraficos.hora_dia.valores, 'Acidentes por Hora do Dia', 'rgba(153, 102, 255, 0.8)');
    criarGrafico(refs.tipo, instances.tipo, 'bar', dadosGraficos.tipo.tipos, dadosGraficos.tipo.valores, 'Tipos de Acidente', 'rgba(255, 99, 132, 0.8)');
    criarGrafico(refs.natureza, instances.natureza, 'bar', dadosGraficos.natureza.naturezas, dadosGraficos.natureza.valores, 'Natureza dos Acidentes', 'rgba(255, 206, 86, 0.8)');
    criarGrafico(refs.veiculos, instances.veiculos, 'bar', dadosGraficos.veiculos.tipos, dadosGraficos.veiculos.valores, 'Tipos de Veículos Envolvidos', 'rgba(54, 162, 235, 0.8)');

    criarHeatmap(refs.heatmap, instances.heatmap, dadosGraficos.heatmap_turno, dadosGraficos.heatmap_turno_dias, dadosGraficos.heatmap_turno_turnos);
  }, [dadosGraficos, darkMode]);

  return (
    <div className={`container-fluid py-4 ${darkMode ? 'bg-dark text-light' : 'bg-light'}`}>
      <div className="text-center mb-4">
        <h1 className="display-5 fw-bold">📊 Previsão de Acidentes de Trânsito</h1>
        <button
          className={`btn btn-${darkMode ? 'outline-light' : 'dark'} mt-2`}
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? '🌞 Modo Claro' : '🌙 Modo Escuro'}
        </button>
      </div>

      {error && <div className="alert alert-danger text-center">{error}</div>}

      {previsaoProximoDia && !error && (
        <div className="alert alert-info text-center fs-5">
          📅 Previsão de acidentes para o próximo dia: <strong>{previsaoProximoDia}</strong>
        </div>
      )}

      <div className="row">
        {[
          { ref: refs.ano },
          { ref: refs.dia },
          { ref: refs.bairros },
          { ref: refs.hora },
          { ref: refs.tipo },
          { ref: refs.natureza },
          { ref: refs.veiculos },
        ].map((item, idx) => (
          <div key={idx} className="col-md-6 mb-4">
            <div className={`card shadow-sm h-100 ${darkMode ? 'bg-secondary text-light' : ''}`}>
              <div className="card-body">
                <div >
                  <canvas ref={item.ref} />
                </div>
              </div>
            </div>
          </div>
        ))}

        <div className="col-12 mb-5">
          <div className={`card shadow border-0 ${darkMode ? 'bg-secondary text-light' : ''}`}>
            <div className="card-header fs-5 fw-semibold">
              🔥 Mapa de Calor: Acidentes por Turno e Dia da Semana
            </div>
            <div className="card-body">
              <canvas ref={refs.heatmap} style={{ height: '400px' }} />
            </div>
          </div>
        </div>
      </div>

      <div className="mb-5">
        <h3 className="mb-3">📚 Histórico de Previsões</h3>
        <div className="table-responsive">
          <table className={`table table-hover table-bordered ${darkMode ? 'table-dark' : ''}`}>
            <thead className={darkMode ? 'table-secondary' : 'table-light'}>
              <tr>
                <th>Data</th>
                <th>Previsão de Acidentes</th>
              </tr>
            </thead>
            <tbody>
              {previsoesHistorico.map((item) => (
                <tr key={item.id}>
                  <td>{item.data}</td>
                  <td>{item.previsao}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;
