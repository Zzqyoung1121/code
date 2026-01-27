const api = require("../../utils/api")

Page({
  data: {
    classId: "",
    images: []
  },
  onLoad() {
    const classId = wx.getStorageSync("classId")
    if (classId) {
      this.setData({ classId: String(classId) })
    }
  },
  onClassIdInput(event) {
    this.setData({ classId: event.detail.value })
  },
  chooseImage() {
    if (!this.data.classId) {
      wx.showToast({ title: "请先填写班级 ID", icon: "none" })
      return
    }
    wx.chooseImage({
      count: 5,
      sourceType: ["camera", "album"],
      success: (res) => {
        const uploadTasks = res.tempFilePaths.map((path) =>
          api.uploadFile({
            url: `/images/upload?class_id=${this.data.classId}`,
            filePath: path
          })
        )
        Promise.all(uploadTasks).then((uploaded) => {
          this.setData({ images: [...this.data.images, ...uploaded] })
          wx.showToast({ title: "上传完成" })
        }).catch(() => {
          wx.showToast({ title: "上传失败", icon: "none" })
        })
      }
    })
  },
  goConfirm(event) {
    const imageId = event.currentTarget.dataset.imageId
    wx.navigateTo({ url: `/pages/confirm/confirm?imageId=${imageId}&classId=${this.data.classId}` })
  }
})
