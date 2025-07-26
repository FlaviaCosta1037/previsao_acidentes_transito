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

    const backgroundColors = Array.isArray(cor) ? cor : cor;
    const borderColors = Array.isArray(cor) ? cor : cor;

    const configBase = {
      labels,
      datasets: [
        {
          label,
          data: dados,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 1,
        },
      ],
    };

    const optionsBase = getChartOptions(darkMode);

    let specificOptions = {};

    if (tipo === "horizontalBar") {
      specificOptions = {
        indexAxis: "y",
        ...optionsBase,
        scales: {
          x: {
            beginAtZero: true,
            ticks: { color: darkMode ? "white" : "black" },
            grid: { color: darkMode ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)" },
          },
          y: {
            ticks: { color: darkMode ? "white" : "black" },
            grid: { color: darkMode ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)" },
          },
        },
      };
      tipo = "bar";
    } else if (tipo === "doughnut" || tipo === "pie") {
      specificOptions = {
        responsive: true,
        plugins: {
          tooltip: { enabled: true },
          legend: {
            position: "top",
            labels: { color: darkMode ? "white" : "black" },
          },
          title: {
            display: !!label,
            text: label,
            color: darkMode ? "white" : "black",
            font: { size: 16, weight: "bold" },
          },
        },
      };
    } else {
      specificOptions = optionsBase;
    }

    instanceRef.current = new Chart(ref.current, {
      type: tipo,
      data: configBase,
      options: specificOptions,
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

  useEffect(() => {
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
        "line", // mudou para linha
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
        "horizontalBar", 
        b.bairros,
        b.valores,
        "Top 10 Bairros",
        "rgba(255,159,64,0.8)"
      );
    if (h?.horas && h?.valores)
      criarGrafico(
        refs.hora,
        instances.hora,
        "line", // linha para hora
        h.horas.map((x) => `${x}h`),
        h.valores,
        "Acidentes por Hora",
        "rgba(153,102,255,0.8)"
      );
    if (t?.tipos && t?.valores)
      criarGrafico(
        refs.tipo,
        instances.tipo,
        "bar", // doughnut
        t.tipos,
        t.valores,
        "Tipos de Acidente",
        [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
          "#C9CBCF",
          "#FF6666",
          "#66FF66",
          "#6666FF",
        ]
      );
    if (n?.naturezas && n?.valores)
      criarGrafico(
        refs.natureza,
        instances.natureza,
        "bar", // pizza
        n.naturezas,
        n.valores,
        "Natureza",
        [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
          "#C9CBCF",
          "#FF6666",
          "#66FF66",
          "#6666FF",
        ]
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
    <div
      className={`container-fluid py-4 ${
        darkMode ? "bg-dark text-light" : "bg-light"
      }`}
    >
      <div className="text-center mb-4">
        <h1 className="display-5 fw-bold">📊 Previsão de Acidentes de Trânsito</h1>
        <button
          className={`btn btn-${darkMode ? "outline-light" : "dark"} mt-2`}
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? "🌞 Modo Claro" : "🌙 Modo Escuro"}
        </button>
      </div>

      {loading && (
        <div className="alert alert-secondary text-center">Carregando…</div>
      )}
      {error && <div className="alert alert-danger text-center">{error}</div>}

      {previsaoProximoDia !== null && (
        <div className="alert alert-info text-center fs-6">
          📅 (Treino/Teste) Próximo dia após fim da base:{" "}
          <strong>{previsaoProximoDia}</strong>
        </div>
      )}

      {/* Gráfico Previsão (só previsão do Firebase) + Erros */}
      {previsoesHistorico.length > 0 && (
        <div className={`card mb-4 shadow ${darkMode ? "bg-secondary text-light" : ""}`}>
          <div className="card-header fw-semibold fs-5">📈 Previsão</div>
          <div
            className="card-body"
            style={{ maxHeight: "400px", overflowY: "auto" }}
          >
            <canvas
              ref={refs.previsaoReal}
              style={{ maxHeight: "250px", width: "100%" }}
            />

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
                    <td>
                      {Number(errosModelo.MAE ?? errosModelo["MAE"])?.toFixed(4)}
                    </td>
                  </tr>
                  <tr>
                    <td>MSE</td>
                    <td>
                      {Number(errosModelo.MSE ?? errosModelo["MSE"])?.toFixed(4)}
                    </td>
                  </tr>
                  <tr>
                    <td>RMSE</td>
                    <td>
                      {Number(errosModelo.RMSE ?? errosModelo["RMSE"])?.toFixed(4)}
                    </td>
                  </tr>
                  <tr>
                    <td>SMAPE</td>
                    <td>
                      {Number(errosModelo.SMAPE ?? errosModelo["SMAPE"])?.toFixed(2)}%
                    </td>
                  </tr>
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Gráficos principais */}
      <div className="row g-3">
        <div className="col-12 col-md-6 col-lg-4">
          <div
            className={`card shadow h-100 ${
              darkMode ? "bg-secondary text-light" : ""
            }`}
          >
            <div className="card-header fw-semibold">📅 Acidentes por Ano</div>
            <div className="card-body" style={{ height: "280px" }}>
              <canvas ref={refs.ano} />
            </div>
          </div>
        </div>

        <div className="col-12 col-md-6 col-lg-4">
          <div
            className={`card shadow h-100 ${
              darkMode ? "bg-secondary text-light" : ""
            }`}
          >
            <div className="card-header fw-semibold">📅 Acidentes por Dia</div>
            <div className="card-body" style={{ height: "280px" }}>
              <canvas ref={refs.dia} />
            </div>
          </div>
        </div>

        <div className="col-12 col-md-6 col-lg-4">
          <div
            className={`card shadow h-100 ${
              darkMode ? "bg-secondary text-light" : ""
            }`}
          >
            <div className="card-header fw-semibold">🏘️ Top 10 Bairros</div>
            <div className="card-body" style={{ height: "320px" }}>
              <canvas ref={refs.bairros} />
            </div>
          </div>
        </div>

        <div className="col-12 col-md-6 col-lg-4">
          <div
            className={`card shadow h-100 ${
              darkMode ? "bg-secondary text-light" : ""
            }`}
          >
            <div className="card-header fw-semibold">⏰ Acidentes por Hora</div>
            <div className="card-body" style={{ height: "280px" }}>
              <canvas ref={refs.hora} />
            </div>
          </div>
        </div>

        <div className="col-12 col-md-6 col-lg-4">
          <div
            className={`card shadow h-100 ${
              darkMode ? "bg-secondary text-light" : ""
            }`}
          >
            <div className="card-header fw-semibold">🚦 Tipos de Acidente</div>
            <div className="card-body" style={{ height: "280px" }}>
              <canvas ref={refs.tipo} />
            </div>
          </div>
        </div>

        <div className="col-12 col-md-6 col-lg-4">
          <div
            className={`card shadow h-100 ${
              darkMode ? "bg-secondary text-light" : ""
            }`}
          >
            <div className="card-header fw-semibold">📋 Natureza</div>
            <div className="card-body" style={{ height: "280px" }}>
              <canvas ref={refs.natureza} />
            </div>
          </div>
        </div>

        <div className="col-12 col-md-6 col-lg-4">
          <div
            className={`card shadow h-100 ${
              darkMode ? "bg-secondary text-light" : ""
            }`}
          >
            <div className="card-header fw-semibold">🚗 Veículos Envolvidos</div>
            <div className="card-body" style={{ height: "280px" }}>
              <canvas ref={refs.veiculos} />
            </div>
          </div>
        </div>

        <div className="col-12 col-md-6 col-lg-8">
          <div
            className={`card shadow h-100 ${
              darkMode ? "bg-secondary text-light" : ""
            }`}
          >
            <div className="card-header fw-semibold">
              🔥 Mapa de Calor: Acidentes por Turno e Dia da Semana
            </div>
            <div className="card-body" style={{ height: "360px" }}>
              <canvas ref={refs.heatmap} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
