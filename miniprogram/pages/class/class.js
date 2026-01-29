const api = require("../../utils/api")

Page({
  data: {
    className: "",
    classId: null
  },
  onLoad() {
    const classId = wx.getStorageSync("classId")
    if (classId) {
      this.setData({ classId })
    }
  },
  onClassInput(event) {
    this.setData({ className: event.detail.value })
  },
  createClass() {
    if (!this.data.className) {
      wx.showToast({ title: "请输入班级名称", icon: "none" })
      return
    }
    api.request({
      url: "/classes",
      method: "POST",
      data: { name: this.data.className }
    }).then((res) => {
      this.setData({ classId: res.id })
      wx.setStorageSync("classId", res.id)
      wx.showToast({ title: "创建成功" })
    }).catch(() => {
      wx.showToast({ title: "创建失败", icon: "none" })
    })
  },
  chooseFile() {
    if (!this.data.classId) {
      wx.showToast({ title: "请先创建班级", icon: "none" })
      return
    }
    wx.chooseMessageFile({
      count: 1,
      type: "file",
      success: (res) => {
        const filePath = res.tempFiles[0].path
        api.uploadFile({
          url: `/students/import?class_id=${this.data.classId}`,
          filePath
        }).then(() => {
          wx.showToast({ title: "导入成功" })
        }).catch(() => {
          wx.showToast({ title: "导入失败", icon: "none" })
        })
      }
    })
  }
})
