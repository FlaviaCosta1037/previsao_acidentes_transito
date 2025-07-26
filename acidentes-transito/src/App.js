import React, { useEffect, useRef, useState } from "react";
import { db } from "./firebase";
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
} from "chart.js";
import { MatrixController, MatrixElement } from "chartjs-chart-matrix";
import "bootstrap/dist/css/bootstrap.min.css";
import { doc, getDoc } from "firebase/firestore";

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
  const [loading, setLoading] = useState(true);

  const [previsaoProximoDia, setPrevisaoProximoDia] = useState(null);
  const [previsoesHistorico, setPrevisoesHistorico] = useState([]);
  const [errosModelo, setErrosModelo] = useState(null);

  const [dadosGraficos, setDadosGraficos] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  // Refs para canvas dos gráficos
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

  // Instâncias Chart.js para destruição antes de redesenhar
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

  function destroyAllCharts() {
    Object.values(instances).forEach((instRef) => {
      if (instRef.current) {
        instRef.current.destroy();
        instRef.current = null;
      }
    });
  }

  function getChartOptions(dark) {
    return {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        tooltip: { enabled: true },
        legend: {
          position: "top",
          labels: { color: dark ? "white" : "black" },
        },
      },
      scales: {
        x: {
          ticks: { color: dark ? "white" : "black" },
          grid: { color: dark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)" },
        },
        y: {
          beginAtZero: true,
          ticks: { color: dark ? "white" : "black" },
          grid: { color: dark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)" },
        },
      },
    };
  }

  function criarGraficoPrevisao(reais, previsoes) {
    if (!refs.previsaoReal.current) return;
    if (instances.previsaoReal.current) instances.previsaoReal.current.destroy();

    const labels = reais.map((_, i) => `Passo ${i + 1}`);

    instances.previsaoReal.current = new Chart(refs.previsaoReal.current, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Real",
            data: reais,
            borderColor: "royalblue",
            backgroundColor: "royalblue",
            fill: false,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
          {
            label: "Previsão",
            data: previsoes,
            borderColor: "firebrick",
            backgroundColor: "firebrick",
            fill: false,
            borderDash: [6, 3],
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
        ],
      },
      options: getChartOptions(darkMode),
    });
  }

  function criarGrafico(ref, instanceRef, tipo, labels, dados, label, cor) {
    if (!ref.current) return;
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
    if (!ref.current) return;
    if (instanceRef.current) instanceRef.current.destroy();

    const matrixData = data.flatMap((row, y) =>
      row.map((value, x) => ({ x: turnos[x], y: dias[y], v: value }))
    );

    instanceRef.current = new Chart(ref.current, {
      type: "matrix",
      data: {
        datasets: [
          {
            label: "Acidentes por Turno e Dia da Semana",
            data: matrixData,
            backgroundColor: (ctx) => {
              const value = ctx.raw.v;
              const max = Math.max(...data.flat());
              const lightness = 90 - 50 * (value / (max || 1));
              return `hsl(210, 100%, ${lightness}%)`;
            },
            width: (ctx) => {
              const chartArea = ctx.chart.chartArea;
              if (!chartArea) return 40;
              return Math.min(
                (chartArea.right - chartArea.left) / turnos.length - 4,
                80
              );
            },
            height: (ctx) => {
              const chartArea = ctx.chart.chartArea;
              if (!chartArea) return 40;
              return Math.min(
                (chartArea.bottom - chartArea.top) / dias.length - 4,
                40
              );
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
            type: "category",
            labels: turnos,
            position: "top",
            ticks: {
              font: { size: 12, weight: "bold" },
              maxRotation: 0,
              minRotation: 0,
              autoSkip: false,
              align: "center",
              padding: 10,
              color: darkMode ? "white" : "black",
            },
            grid: { drawOnChartArea: false },
          },
          y: {
            type: "category",
            labels: dias,
            ticks: { font: { size: 12 }, color: darkMode ? "white" : "black" },
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
            text: "Mapa de Calor: Acidentes por Turno e Dia da Semana",
            font: { size: 16, weight: "bold" },
          },
        },
      },
    });
  }

  // Busca dados do Firebase para previsões e erros
  useEffect(() => {
    async function buscarDadosFirebase() {
      setLoading(true);
      try {
        const docRef = doc(db, "previsoes", "ultimo_modelo");
        const docSnap = await getDoc(docRef);

        if (docSnap.exists()) {
          const data = docSnap.data();
          setPrevisoesHistorico(data.previsoes || []);
          setErrosModelo(data.erros || null);
          setPrevisaoProximoDia(data.previsoes?.[0]?.valor || null);
        } else {
          setError("Documento 'ultimo_modelo' não encontrado no Firebase.");
        }
      } catch (e) {
        setError("Erro ao buscar dados do Firebase: " + e.message);
      } finally {
        setLoading(false);
      }
    }
    buscarDadosFirebase();
  }, []);

  // Busca dados da API para demais gráficos
  useEffect(() => {
    async function buscarDadosGraficos() {
      try {
        const res = await fetch("http://127.0.0.1:5000/api/graficos");
        if (!res.ok) throw new Error("Erro ao buscar dados dos gráficos");
        const json = await res.json();
        setDadosGraficos(json);
      } catch (e) {
        setError(e.message);
      }
    }
    buscarDadosGraficos();
  }, []);

  // Atualiza gráfico Previsão vs Real (você precisa fornecer série real e série previsão aqui, se quiser)
  // Como você salva só previsões no Firebase, aqui deixei só a previsão histórica
  // Se você tiver série real, precisa buscar e setar no estado também para mostrar no gráfico
  useEffect(() => {
    // Para exemplo simples, vou criar gráfico só com valores previstos
    if (!previsoesHistorico.length) {
      if (instances.previsaoReal.current) {
        instances.previsaoReal.current.destroy();
        instances.previsaoReal.current = null;
      }
      return;
    }

    const labels = previsoesHistorico.map((item) =>
      item.data ? new Date(item.data).toLocaleDateString("pt-BR") : "?"
    );
    const dados = previsoesHistorico.map((item) => item.valor);

    if (!refs.previsaoReal.current) return;
    if (instances.previsaoReal.current) instances.previsaoReal.current.destroy();

    instances.previsaoReal.current = new Chart(refs.previsaoReal.current, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Previsão",
            data: dados,
            borderColor: "firebrick",
            backgroundColor: "firebrick",
            fill: false,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
        ],
      },
      options: getChartOptions(darkMode),
    });
  }, [previsoesHistorico, darkMode]);

  // Atualiza demais gráficos
  useEffect(() => {
    if (!dadosGraficos) return;

    const a = dadosGraficos?.acidentes_ano;
    const d = dadosGraficos?.acidentes_dia;
    const b = dadosGraficos?.top_bairros;
    const h = dadosGraficos?.hora_dia;
    const t = dadosGraficos?.tipo;
    const n = dadosGraficos?.natureza;
    const v = dadosGraficos?.veiculos;

    if (a?.anos && a?.valores)
      criarGrafico(
        refs.ano,
        instances.ano,
        "bar",
        a.anos,
        a.valores,
        "Acidentes por Ano",
        "rgba(54,162,235,0.8)"
      );
    if (d?.dias && d?.valores)
      criarGrafico(
        refs.dia,
        instances.dia,
        "bar",
        d.dias,
        d.valores,
        "Acidentes por Dia",
        "rgba(75,192,192,0.8)"
      );
    if (b?.bairros && b?.valores)
      criarGrafico(
        refs.bairros,
        instances.bairros,
        "bar",
        b.bairros,
        b.valores,
        "Top 10 Bairros",
        "rgba(255,159,64,0.8)"
      );
    if (h?.horas && h?.valores)
      criarGrafico(
        refs.hora,
        instances.hora,
        "bar",
        h.horas.map((x) => `${x}h`),
        h.valores,
        "Acidentes por Hora",
        "rgba(153,102,255,0.8)"
      );
    if (t?.tipos && t?.valores)
      criarGrafico(
        refs.tipo,
        instances.tipo,
        "bar",
        t.tipos,
        t.valores,
        "Tipos de Acidente",
        "rgba(255,99,132,0.8)"
      );
    if (n?.naturezas && n?.valores)
      criarGrafico(
        refs.natureza,
        instances.natureza,
        "bar",
        n.naturezas,
        n.valores,
        "Natureza",
        "rgba(255,206,86,0.8)"
      );
    if (v?.tipos && v?.valores)
      criarGrafico(
        refs.veiculos,
        instances.veiculos,
        "bar",
        v.tipos,
        v.valores,
        "Veículos Envolvidos",
        "rgba(54,162,235,0.8)"
      );

    if (
      Array.isArray(dadosGraficos?.heatmap_turno) &&
      Array.isArray(dadosGraficos?.heatmap_turno_dias) &&
      Array.isArray(dadosGraficos?.heatmap_turno_turnos)
    ) {
      criarHeatmap(
        refs.heatmap,
        instances.heatmap,
        dadosGraficos.heatmap_turno,
        dadosGraficos.heatmap_turno_dias,
        dadosGraficos.heatmap_turno_turnos
      );
    }
  }, [dadosGraficos, darkMode]);

  return (
    <div className={`container-fluid py-4 ${darkMode ? "bg-dark text-light" : "bg-light"}`}>
      <div className="text-center mb-4">
        <h1 className="display-5 fw-bold">📊 Previsão de Acidentes de Trânsito</h1>
        <button
          className={`btn btn-${darkMode ? "outline-light" : "dark"} mt-2`}
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? "🌞 Modo Claro" : "🌙 Modo Escuro"}
        </button>
      </div>

      {loading && <div className="alert alert-secondary text-center">Carregando…</div>}
      {error && <div className="alert alert-danger text-center">{error}</div>}

      {previsaoProximoDia !== null && (
        <div className="alert alert-info text-center fs-6">
          📅 (Treino/Teste) Próximo dia após fim da base: <strong>{previsaoProximoDia}</strong>
        </div>
      )}

      {/* Gráfico Previsão (só previsão do Firebase) + Erros */}
      {previsoesHistorico.length > 0 && (
  <div className={`card mb-4 shadow ${darkMode ? "bg-secondary text-light" : ""}`}>
    <div className="card-header fw-semibold fs-5">📈 Previsão</div>
    <div className="card-body" style={{ maxHeight: "400px", overflowY: "auto" }}>
      <canvas ref={refs.previsaoReal} style={{ maxHeight: "250px", width: "100%" }} />
      
      {errosModelo && (
        <table className={`table mt-3 ${darkMode ? "table-dark" : ""}`}>
          <thead>
            <tr>
              <th>Erro</th>
              <th>Valor</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>MAE</td>
              <td>{Number(errosModelo.MAE ?? errosModelo["MAE"])?.toFixed(4)}</td>
            </tr>
            <tr>
              <td>MSE</td>
              <td>{Number(errosModelo.MSE ?? errosModelo["MSE"])?.toFixed(4)}</td>
            </tr>
            <tr>
              <td>RMSE</td>
              <td>{Number(errosModelo.RMSE ?? errosModelo["RMSE"])?.toFixed(4)}</td>
            </tr>
            <tr>
              <td>MAPE (%)</td>
              <td>{Number(errosModelo["MAPE (%)"] ?? errosModelo.MAPE)?.toFixed(2)}%</td>
            </tr>
          </tbody>
        </table>
      )}

      <h5 className="mt-4">📅 Histórico das Previsões</h5>
      <table className={`table ${darkMode ? "table-dark" : ""}`}>
        <thead>
          <tr>
            <th>Data</th>
            <th>Valor</th>
          </tr>
        </thead>
        <tbody>
          {previsoesHistorico.map((item, index) => (
            <tr key={index}>
              <td>{item.data ? new Date(item.data).toLocaleDateString("pt-BR") : "-"}</td>
              <td>{item.valor}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
)}


      {/* Outros gráficos */}
      <div className="row">
        {[{ ref: refs.ano, title: "Acidentes por Ano" },
        { ref: refs.dia, title: "Acidentes por Dia" },
        { ref: refs.bairros, title: "Top 10 Bairros" },
        { ref: refs.hora, title: "Acidentes por Hora" },
        { ref: refs.tipo, title: "Tipos de Acidente" },
        { ref: refs.natureza, title: "Natureza" },
        { ref: refs.veiculos, title: "Veículos Envolvidos" }].map((item, i) => (
          <div key={i} className="col-md-6 mb-4">
            <div className={`card shadow-sm h-100 ${darkMode ? "bg-secondary text-light" : ""}`}>
              <div className="card-header fw-semibold">{item.title}</div>
              <div className="card-body">
                <canvas ref={item.ref} />
              </div>
            </div>
          </div>
        ))}

        <div className="col-12 mb-5">
          <div className={`card shadow border-0 ${darkMode ? "bg-secondary text-light" : ""}`}>
            <div className="card-header fs-5 fw-semibold">🔥 Mapa de Calor</div>
            <div className="card-body" style={{ height: "400px" }}>
              <canvas ref={refs.heatmap} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
