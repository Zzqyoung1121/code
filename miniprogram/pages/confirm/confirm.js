const api = require("../../utils/api")

Page({
  data: {
    classId: "",
    imageId: "",
    taskId: "",
    recognizedText: "",
    candidates: []
  },
  onLoad(options) {
    const storedTaskId = wx.getStorageSync("taskId")
    this.setData({
      classId: options.classId || "",
      imageId: options.imageId || "",
      taskId: storedTaskId ? String(storedTaskId) : ""
    })
  },
  onTextInput(event) {
    this.setData({ recognizedText: event.detail.value })
  },
  onTaskInput(event) {
    this.setData({ taskId: event.detail.value })
  },
  runOcr() {
    if (!this.data.classId || !this.data.imageId) {
      wx.showToast({ title: "缺少班级或图片", icon: "none" })
      return
    }
    api.request({
      url: "/ocr/recognize",
      method: "POST",
      data: {
        class_id: Number(this.data.classId),
        image_id: Number(this.data.imageId),
        recognized_text: this.data.recognizedText
      }
    }).then((res) => {
      this.setData({ candidates: res.candidates || [] })
      wx.showToast({ title: "识别完成" })
    }).catch(() => {
      wx.showToast({ title: "识别失败", icon: "none" })
    })
  },
  confirmSubmit(event) {
    if (!this.data.taskId) {
      wx.showToast({ title: "请先填写任务 ID", icon: "none" })
      return
    }
    const studentId = event.currentTarget.dataset.studentId
    api.request({
      url: "/submissions/confirm",
      method: "POST",
      data: {
        task_id: Number(this.data.taskId),
        student_id: Number(studentId),
        image_id: Number(this.data.imageId),
        status: "submitted",
        source: "manual"
      }
    }).then(() => {
      wx.showToast({ title: "已确认" })
    }).catch(() => {
      wx.showToast({ title: "确认失败", icon: "none" })
    })
  }
})
