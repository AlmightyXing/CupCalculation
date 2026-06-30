const BASE_URL = 'http://127.0.0.1:8000'; // 暂定本地FastAPI地址

/**
 * 封装微信小程序的网络请求
 */
function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          // 可以在此统一处理错误提示
          wx.showToast({
            title: res.data.message || '请求失败',
            icon: 'none'
          });
          reject(res);
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络异常',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
}

export default {
  get(url, data, header) {
    return request(url, { method: 'GET', data, header });
  },
  post(url, data, header) {
    return request(url, { method: 'POST', data, header });
  }
}
