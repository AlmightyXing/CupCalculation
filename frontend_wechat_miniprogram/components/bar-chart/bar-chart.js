import * as echarts from '../../ec-canvas/echarts';

Component({
  properties: {
    chartData: {
      type: Object,
      value: null,
      observer(newVal) {
        if (newVal && this.chart) {
          this.initChart(this.chart, newVal);
        }
      }
    }
  },
  data: {
    ec: {
      lazyLoad: true
    }
  },
  ready() {
    this.ecComponent = this.selectComponent('#mychart-dom-bar');
    if (this.data.chartData) {
      this.init();
    }
  },
  methods: {
    init() {
      this.ecComponent.init((canvas, width, height, dpr) => {
        const chart = echarts.init(canvas, null, {
          width: width,
          height: height,
          devicePixelRatio: dpr
        });
        this.chart = chart;
        this.initChart(chart, this.data.chartData);
        return chart;
      });
    },
    initChart(chart, data) {
      if(!data || !data.categories) return;
      const option = {
        backgroundColor: '#121212',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        grid: {
          left: '3%',
          right: '8%',
          bottom: '3%',
          top: '5%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          axisLabel: { color: '#AAAAAA' },
          splitLine: { lineStyle: { color: '#333333' } }
        },
        yAxis: {
          type: 'category',
          data: data.categories,
          axisLabel: { color: '#FFFFFF', fontWeight: 'bold' }
        },
        series: [
          {
            type: 'bar',
            data: data.values,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                { offset: 0, color: '#D32F2F' },
                { offset: 1, color: '#FF7043' }
              ]),
              borderRadius: [0, 4, 4, 0]
            },
            label: {
              show: true,
              position: 'right',
              color: '#FFFFFF'
            }
          }
        ]
      };
      chart.setOption(option);
    }
  }
});
