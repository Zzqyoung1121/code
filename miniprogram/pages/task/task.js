const api = require("../../utils/api")

Page({
  data: {
    classId: "",
    subject: "",
    notes: "",
    taskId: null
  },
  onLoad() {
    const classId = wx.getStorageSync("classId")
    const taskId = wx.getStorageSync("taskId")
    if (classId) {
      this.setData({ classId: String(classId) })
    }
    if (taskId) {
      this.setData({ taskId })
    }
  },
  onClassIdInput(event) {
    this.setData({ classId: event.detail.value })
  },
  onSubjectInput(event) {
    this.setData({ subject: event.detail.value })
  },
  onNotesInput(event) {
    this.setData({ notes: event.detail.value })
  },
  createTask() {
    if (!this.data.classId || !this.data.subject) {
      wx.showToast({ title: "请填写班级 ID 和科目", icon: "none" })
      return
    }
    api.request({
      url: "/homework_tasks",
      method: "POST",
      data: {
        class_id: Number(this.data.classId),
        subject: this.data.subject,
        notes: this.data.notes
      }
    }).then((res) => {
      this.setData({ taskId: res.id })
      wx.setStorageSync("taskId", res.id)
      wx.showToast({ title: "创建成功" })
    }).catch(() => {
      wx.showToast({ title: "创建失败", icon: "none" })
    })
  }
})
