import { ElMessageBox, ElMessage } from 'element-plus'

export interface ConfirmDialogOptions {
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  type?: 'warning' | 'error' | 'info' | 'success'
}

export const showConfirmDialog = async (options: ConfirmDialogOptions = {}) => {
  const {
    title = '确认操作',
    message = '确定要执行此操作吗？',
    confirmText = '确认',
    cancelText = '取消',
    type = 'warning'
  } = options

  return ElMessageBox.confirm(message, title, {
    confirmButtonText: confirmText,
    cancelButtonText: cancelText,
    type,
    center: true,
    closeOnClickModal: false,
    closeOnPressEscape: true,
    customClass: 'custom-confirm-dialog',
    confirmButtonClass: 'el-button--danger'
  })
}

export const showDeleteConfirm = async (itemName: string = '此记录') => {
  return showConfirmDialog({
    title: '确认删除',
    message: `确定要删除${itemName}吗？删除后无法恢复。`,
    confirmText: '删除',
    cancelText: '取消',
    type: 'warning'
  })
}

export const showMessage = {
  success: (message: string) => {
    ElMessage({
      message,
      type: 'success',
      duration: 3000,
      center: true
    })
  },
  error: (message: string) => {
    ElMessage({
      message,
      type: 'error',
      duration: 4000,
      center: true
    })
  },
  warning: (message: string) => {
    ElMessage({
      message,
      type: 'warning',
      duration: 3500,
      center: true
    })
  },
  info: (message: string) => {
    ElMessage({
      message,
      type: 'info',
      duration: 3000,
      center: true
    })
  }
}
