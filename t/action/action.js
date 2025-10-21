
document.addEventListener('DOMContentLoaded', () => {
    const chartCanvas = document.getElementById('trading-chart');
    let chart;

    const coinList = document.querySelector('.coin-list');
    coinList.addEventListener('click', (event) => {
        if (event.target.tagName === 'LI') {
            const coinId = event.target.dataset.coin;
            fetchCoinData(coinId);
        }
    });

    function createFavicon() {
        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#4CAF50';
        ctx.beginPath();
        ctx.arc(16, 16, 14, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 16px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('K', 16, 16);
        document.getElementById('favicon').href = canvas.toDataURL();
    }

    async function fetchCoinData(coinId) {
        try {
            const response = await fetch(`https://api.coingecko.com/api/v3/coins/${coinId}/ohlc?vs_currency=usd&days=30`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            updateChart(data, coinId);
        } catch (error) {
            console.error('Error fetching coin data:', error);
            alert('Failed to fetch cryptocurrency data. The API may be temporarily unavailable.');
        }
    }

    function updateChart(data, coinId) {
        if (chart) {
            chart.destroy();
        }

        const chartData = data.map(d => ({
            x: d[0],
            o: d[1],
            h: d[2],
            l: d[3],
            c: d[4]
        }));

        const ctx = chartCanvas.getContext('2d');
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                datasets: [{
                    label: `${coinId.charAt(0).toUpperCase() + coinId.slice(1)} (USD)`,
                    data: chartData,
                    backgroundColor: (ctx) => {
                        const { o, c } = ctx.raw;
                        return c >= o ? 'rgba(75, 192, 192, 0.5)' : 'rgba(255, 99, 132, 0.5)';
                    },
                    borderColor: (ctx) => {
                        const { o, c } = ctx.raw;
                        return c >= o ? 'rgb(75, 192, 192)' : 'rgb(255, 99, 132)';
                    },
                    borderWidth: 1,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0,
                }]
            },
            options: {
                 parsing: {
                    xAxisKey: 'x',
                    yAxisKey: 's'
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const d = context.raw;
                                let label = `${context.dataset.label}:`;
                                if (label) {
                                    label += ' ';
                                }
                                return `${label} O: ${d.o}, H: ${d.h}, L: ${d.l}, C: ${d.c}`;
                            }
                        }
                    }
                }
            }
        });
    }

    createFavicon();
    fetchCoinData('bitcoin'); // Load bitcoin by default
});
