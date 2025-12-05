<template>
  <div class="container">
    <Menu></Menu>
    <div class="content">
      <h1>历史数据查看</h1>
      <el-row>
        <el-col :span="24">
          <div class="grid-content bg-purple-dark">
            <el-form :inline="true" :model="form" size="small" ref="ruleForm" class="demo-form-inline" style="margin-left: 10px">
              <el-form-item label="创建日期" prop="create_date">
                <el-date-picker
                  v-model="form.create_date"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="yyyy-MM-dd"
                  :default-time="['00:00:00', '23:59:59']">
                </el-date-picker>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submitForm('ruleForm')" size="small">查询</el-button>
                <el-button @click="resetForm('ruleForm')" size="small">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>
      </el-row>
      <el-table
        :data="pagedTableData"
        border
        height="350"
        style="width: 100%; margin-top: 30px;margin-left: 10px"
      >
        <el-table-column
            type="index"
            width="50">
        </el-table-column>
        <el-table-column
            prop="captureTime"
            label="日期"
            width="180"
            align="center">
        </el-table-column>
        <el-table-column
            prop="name"
            label="图片名称"
            width="180"
            align="center">
        </el-table-column>
        <el-table-column
            label="缩略图"
            width="180"
            align="center">
          <template slot-scope="scope">
            <el-image
              style="width: 150px; height: 100px"
              :src="scope.row.hasDefects === '是' ? scope.row.thumbnail : ''"
              :preview-src-list="scope.row.hasDefects === '是' ? [scope.row.image] : []"
            >
              <div slot="error" class="image-slot">
                <span style="color: #67C23A; font-size: 16px; font-weight: bold;">正常</span>
              </div>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column
            prop="hasDefects"
            label="是否有缺陷"
            width="100"
            align="center">
            <template slot-scope="scope">
              {{ scope.row.hasDefects }}
            </template>
        </el-table-column>
        <el-table-column
            prop="detection_total_cnts"
            label="缺陷总数"
            width="100"
            align="center">
        </el-table-column>
        <el-table-column
            prop="detection_classes"
            label="缺陷类别"
            align="center">
            <template slot-scope="scope">
              {{ formatDetectionClasses(scope.row.detection_classes) }}
            </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px; text-align: center;">
        <div style="font-size: 14px; color: #606266; margin-bottom: 10px;">
          共 {{ tableData.length }} 条记录，每页显示
          <el-select v-model="pageSize" size="mini" style="width: 60px; margin: 0 5px;" @change="handleSizeChange">
            <el-option label="10条" :value="10"></el-option>
            <el-option label="25条" :value="25"></el-option>
            <el-option label="50条" :value="50"></el-option>
          </el-select>
        </div>
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 25, 50]"
          :page-size="pageSize"
          layout="prev, pager, next, jumper"
          :total="tableData.length">
        </el-pagination>
      </div>
    </div>
  </div>
</template>

<script>
import Menu from '@/components/Menu.vue' // 确保Menu组件已导入
import { Row as ElRow, Col as ElCol, Form as ElForm, FormItem as ElFormItem, DatePicker as ElDatePicker, Button as ElButton, Table as ElTable, TableColumn as ElTableColumn, Image as ElImage, Pagination as ElPagination, Select as ElSelect, Option as ElOption } from 'element-ui' // 确保Element UI组件已导入
import { getImages } from '@/api/api.js' // 导入API

export default {
  name: 'History',
  components: {
    Menu,
    ElRow,
    ElCol,
    ElForm,
    ElFormItem,
    ElDatePicker,
    ElButton,
    ElTable,
    ElTableColumn,
    ElImage,
    ElPagination,
    ElSelect,
    ElOption
  },
  data () {
    return {
      form: {
        create_date: []
      },
      tableData: [],
      currentPage: 1,
      pageSize: 10
    }
  },
  computed: {
    pagedTableData () {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.tableData.slice(start, end)
    }
  },
  methods: {
    async fetchData () {
      try {
        const [startDate, endDate] = this.form.create_date
        const response = await getImages(startDate, endDate)
        this.tableData = response.data.map(item => ({
          ...item,
          thumbnail: `/api/results/images/${item.name}.png`, // 假设这是静态文件路径
          image: `/api/results/images/${item.name}.png`,
          hasDefects: item.hasDefects === true ? '是' : '否'
        }))
      } catch (error) {
        console.error('Error fetching data:', error)
        // 可以在这里添加更多的错误处理逻辑，例如显示错误提示
      }
    },
    formatDetectionClasses (classes) {
      if (!classes || !Array.isArray(classes) || classes.length === 0) {
        return '无'
      }
      return classes.join(', ')
    },
    submitForm () {
      this.fetchData() // 提交表单后重新加载数据
    },
    resetForm () {
      this.$refs.ruleForm.resetFields()
      this.fetchData() // 重置表单后重新加载数据
    },
    handleSizeChange (val) {
      this.pageSize = val
      this.currentPage = 1
    },
    handleCurrentChange (val) {
      this.currentPage = val
    }
  },
  created () {
    this.fetchData()
  }
}
</script>
