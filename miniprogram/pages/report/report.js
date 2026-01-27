const api = require("../../utils/api")

Page({
  data: {
    taskId: "",
    report: {
      totals: {},
      entries: []
    }
  },
  onTaskInput(event) {
    this.setData({ taskId: event.detail.value })
  },
  loadReport() {
    if (!this.data.taskId) {
      wx.showToast({ title: "请填写任务 ID", icon: "none" })
      return
    }
    api.request({
      url: `/reports/homework/${this.data.taskId}`
    }).then((res) => {
      this.setData({ report: res })
      wx.showToast({ title: "加载成功" })
    }).catch(() => {
      wx.showToast({ title: "加载失败", icon: "none" })
    })
  }
})
