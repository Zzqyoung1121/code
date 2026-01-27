const app = getApp()

const request = (options) => {
  const baseUrl = app.globalData.baseUrl
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${baseUrl}${options.url}`,
      method: options.method || "GET",
      data: options.data || {},
      header: options.header || {"Content-Type": "application/json"},
      success: (res) => resolve(res.data),
      fail: (err) => reject(err)
    })
  })
}

const uploadFile = (options) => {
  const baseUrl = app.globalData.baseUrl
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${baseUrl}${options.url}`,
      filePath: options.filePath,
      name: options.name || "file",
      formData: options.formData || {},
      success: (res) => {
        try {
          resolve(JSON.parse(res.data))
        } catch (error) {
          reject(error)
        }
      },
      fail: (err) => reject(err)
    })
  })
}

module.exports = {
  request,
  uploadFile
}
