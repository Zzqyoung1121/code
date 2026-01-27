Page({
  data: {
    pendingCount: 0,
    latestTask: {
      subject: "暂无"
    }
  },
  goCapture() {
    wx.navigateTo({ url: "/pages/capture/capture" })
  },
  goTasks() {
    wx.navigateTo({ url: "/pages/task/task" })
  },
  goClasses() {
    wx.navigateTo({ url: "/pages/class/class" })
  }
})
