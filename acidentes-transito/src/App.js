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
  LineElement,
  LineController,
} from 'chart.js';
import { MatrixController, MatrixElement } from 'chartjs-chart-matrix';
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
  LineElement,
  LineController,
  MatrixController,
  MatrixElement
);

function App() {
  const [error, setError] = useState(null);
  const [previsaoProximoDia, setPrevisaoProximoDia] = useState(null);
  const [previsoesHistorico, setPrevisoesHistorico] = useState([]);
  const [serieReal, setSerieReal] = useState([]);
  const [seriePrevisao, setSeriePrevisao] = useState([]);
  const [errosModelo, setErrosModelo] = useState(null);
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
    previsaoReal: useRef(null),
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
    previsaoReal: useRef(null),
  };

  // Funções para carregar dados da API
  async function carregarPrevisoesTreino() {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/previsao');
      if (!res.ok) throw new Error('Erro ao buscar previsões (treino/teste)');
      const data = await res.json();
      setPrevisaoProximoDia(data.previsao_proximo_dia);
      setPrevisoesHistorico(data.previsoes_proximos_6_dias || []);
      setSerieReal(data.serie_real || []);
      setSeriePrevisao(data.serie_previsao || []);
      setErrosModelo(data.erros || null);
    } catch (e) {
      setError(e.message);
    }
  }

  async function carregarGraficos() {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/graficos');
      if (!res.ok) throw new Error('Erro ao buscar gráficos');
      setDadosGraficos(await res.json());
    } catch (e) {
      setError(e.message);
    }
  }

  function getChartOptions(darkMode) {
    return {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        tooltip: { enabled: true },
        legend: {
          position: 'top',
          labels: { color: darkMode ? 'white' : 'black' },
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

  function criarGraficoPrevisao(reais, previsoes) {
    if (instances.previsaoReal.current) instances.previsaoReal.current.destroy();
    const labels = reais.map((_, i) => `Passo ${i + 1}`);

    instances.previsaoReal.current = new Chart(refs.previsaoReal.current, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Real',
            data: reais,
            borderColor: 'royalblue',
            backgroundColor: 'royalblue',
            fill: false,
            tension: 0.3,
            pointRadius: 5,
            pointHoverRadius: 7,
          },
          {
            label: 'Previsão',
            data: previsoes,
            borderColor: 'firebrick',
            backgroundColor: 'firebrick',
            fill: false,
            borderDash: [6, 3],
            tension: 0.3,
            pointRadius: 5,
            pointHoverRadius: 7,
          },
        ],
      },
      options: getChartOptions(darkMode),
    });
  }

  function criarGrafico(ref, instanceRef, tipo, labels, dados, label, cor) {
    if (instanceRef.current) instanceRef.current.destroy();

    instanceRef.current = new Chart(ref.current, {
      type: tipo,
      data: {
        labels,
        datasets: [
          {
            label,
            data: dados,
            backgroundColor: cor,
            borderColor: cor,
            borderWidth: 1,
          },
        ],
      },
      options: getChartOptions(darkMode),
    });
  }

  function criarHeatmap(ref, instanceRef, data, dias, turnos) {
    if (instanceRef.current) instanceRef.current.destroy();
    const matrixData = data.flatMap((row, y) =>
      row.map((value, x) => ({ x: turnos[x], y: dias[y], v: value }))
    );
    instanceRef.current = new Chart(ref.current, {
      type: 'matrix',
      data: {
        datasets: [
          {
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
          },
        ],
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
            ticks: {
              font: { size: 12, weight: 'bold' },
              maxRotation: 0,
              minRotation: 0,
              autoSkip: false,
              align: 'center',
              padding: 10,
              color: darkMode ? 'white' : 'black',
            },
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
    carregarGraficos();
    carregarPrevisoesTreino();
  }, []);

  useEffect(() => {
    if (serieReal.length > 0 && seriePrevisao.length > 0) {
      criarGraficoPrevisao(serieReal, seriePrevisao);
    }
  }, [serieReal, seriePrevisao, darkMode]);

  useEffect(() => {
    if (!dadosGraficos) return;

    criarGrafico(refs.ano, instances.ano, 'bar', dadosGraficos.acidentes_ano.anos, dadosGraficos.acidentes_ano.valores, 'Acidentes por Ano', 'rgba(54, 162, 235, 0.8)');
    criarGrafico(refs.dia, instances.dia, 'bar', dadosGraficos.acidentes_dia.dias, dadosGraficos.acidentes_dia.valores, 'Acidentes por Dia', 'rgba(75, 192, 192, 0.8)');
    criarGrafico(refs.bairros, instances.bairros, 'bar', dadosGraficos.top_bairros.bairros, dadosGraficos.top_bairros.valores, 'Top 10 Bairros', 'rgba(255, 159, 64, 0.8)');
    criarGrafico(refs.hora, instances.hora, 'bar', dadosGraficos.hora_dia.horas.map((h) => `${h}h`), dadosGraficos.hora_dia.valores, 'Acidentes por Hora', 'rgba(153, 102, 255, 0.8)');
    criarGrafico(refs.tipo, instances.tipo, 'bar', dadosGraficos.tipo.tipos, dadosGraficos.tipo.valores, 'Tipos de Acidente', 'rgba(255, 99, 132, 0.8)');
    criarGrafico(refs.natureza, instances.natureza, 'bar', dadosGraficos.natureza.naturezas, dadosGraficos.natureza.valores, 'Natureza', 'rgba(255, 206, 86, 0.8)');
    criarGrafico(refs.veiculos, instances.veiculos, 'bar', dadosGraficos.veiculos.tipos, dadosGraficos.veiculos.valores, 'Veículos Envolvidos', 'rgba(54, 162, 235, 0.8)');
    criarHeatmap(refs.heatmap, instances.heatmap, dadosGraficos.heatmap_turno, dadosGraficos.heatmap_turno_dias, dadosGraficos.heatmap_turno_turnos);
  }, [dadosGraficos, darkMode]);

  return (
    <div className={`container-fluid py-4 ${darkMode ? 'bg-dark text-light' : 'bg-light'}`}>
      <div className="text-center mb-4">
        <h1 className="display-5 fw-bold">📊 Previsão de Acidentes de Trânsito</h1>
        <button className={`btn btn-${darkMode ? 'outline-light' : 'dark'} mt-2`} onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? '🌞 Modo Claro' : '🌙 Modo Escuro'}
        </button>
      </div>

      {error && <div className="alert alert-danger text-center">{error}</div>}

      {previsaoProximoDia !== null && (
        <div className="alert alert-info text-center fs-6">
          📅 (Treino/Teste) Próximo dia após fim da base: <strong>{previsaoProximoDia}</strong>
        </div>
      )}

      {serieReal.length > 0 && seriePrevisao.length > 0 && (
        <div className={`card mb-4 shadow ${darkMode ? 'bg-secondary text-light' : ''}`}>
          <div className="card-header fw-semibold fs-5">📈 Previsão vs Real</div>
          <div className="card-body">
            <canvas ref={refs.previsaoReal} />
            {errosModelo && (
              <table className={`table mt-3 ${darkMode ? 'table-dark' : ''}`}>
                <thead>
                  <tr><th>Erro</th><th>Valor</th></tr>
                </thead>
                <tbody>
                  <tr><td>MAE</td><td>{errosModelo.MAE?.toFixed(4)}</td></tr>
                  <tr><td>MSE</td><td>{errosModelo.MSE?.toFixed(4)}</td></tr>
                  <tr><td>RMSE</td><td>{errosModelo.RMSE?.toFixed(4)}</td></tr>
                  <tr><td>MAPE</td><td>{errosModelo.MAPE?.toFixed(2)}%</td></tr>
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      <div className="row">
        {[refs.ano, refs.dia, refs.bairros, refs.hora, refs.tipo, refs.natureza, refs.veiculos].map((ref, i) => (
          <div key={i} className="col-md-6 mb-4">
            <div className={`card shadow-sm h-100 ${darkMode ? 'bg-secondary text-light' : ''}`}>
              <div className="card-body">
                <canvas ref={ref} />
              </div>
            </div>
          </div>
        ))}

        <div className="col-12 mb-5">
          <div className={`card shadow border-0 ${darkMode ? 'bg-secondary text-light' : ''}`}>
            <div className="card-header fs-5 fw-semibold">🔥 Mapa de Calor</div>
            <div className="card-body" style={{ height: '400px' }}>
              <canvas ref={refs.heatmap} />
            </div>
          </div>
        </div>
      </div>

      <div className="mb-5">
        <h3 className="mb-3">📚 Histórico de Previsões (Treino/Teste)</h3>
        <div className="table-responsive">
          <table className={`table table-hover table-bordered ${darkMode ? 'table-dark' : ''}`}>
            <thead className={darkMode ? 'table-secondary' : 'table-light'}>
              <tr><th>Data</th><th>Previsão</th></tr>
            </thead>
            <tbody>
              {previsoesHistorico.map((item, i) => (
                <tr key={i}>
                  <td>{new Date(item.data).toLocaleDateString('pt-BR')}</td>
                  <td>{item.valor}</td>
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
