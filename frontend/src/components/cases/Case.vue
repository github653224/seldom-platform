<!--
/**
* @author bugmaster
* @date 2022-06-11
* @desc 首页/用例管理
*/
-->
<template>
  <div class="case">
    <div style="padding-bottom: 20px; height: 30px;">
      <span class="span-left">
        <span class="page-title">用例管理</span>
      </span>
      <span class="span-breadcrumb">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>用例管理</el-breadcrumb-item>
        </el-breadcrumb>
      </span>
    </div>
    <el-card class="main-card">
      <div style="text-align: left;">
        <el-form :inline="true">
          <el-form-item label="项目">
            <el-select v-model="projectId" placeholder="选择项目" size="small" @change="changeProject()">
              <el-option
                v-for="item in projectOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="syncProject" size="small">同步</el-button>
          </el-form-item>
          <el-form-item label="用例" style="float: right;">
           <el-tag>{{caseNumber}}</el-tag> 条
          </el-form-item>
        </el-form>
      </div>
      <h1>用例列表</h1>
      <div style="min-height: 600px;">
        <div style="width: 20%; float: left;">
          <el-card style="min-height: 500px; overflow: scroll;">
            <el-tree
              :data="fileData"
              node-key="id"
              ref="tree"
              lazy
              highlight-current
              :props="defaultProps"
              @node-click="handleNodeClick"
              >
              <span class="custom-tree-node" slot-scope="{ node, data }">
                <span v-if="data.is_leaf === 1">
                  <i class="el-icon-tickets"></i>
                </span>
                <span v-else>
                  <i class="el-icon-folder"></i>
                </span>
                  {{ data.label }}
              </span>
            </el-tree>
          </el-card>
        </div>
        <div style="width: 78%; float: right">
          <el-table :data="caseData" border  @row-click="caseRowClick" style="width: 100%"  height="500">
            <el-table-column prop="id" label="ID" width="100"> </el-table-column>
            <el-table-column prop="class_name" label="测试类"> </el-table-column>
            <el-table-column prop="class_doc" label="测试类描述"> </el-table-column>
            <el-table-column prop="case_name" label="测试方法"> </el-table-column>
            <el-table-column prop="case_doc" label="测试方法描述"> </el-table-column>
            <el-table-column prop="status" label="状态">
               <template slot-scope="scope">
                <span v-if="scope.row.status === 0">
                  <el-tag type="info"> 未执行 </el-tag>
                </span>
                <span v-else-if="scope.row.status === 1">
                  <el-tag type="success"> 执行中 </el-tag>
                </span>
                <span v-else-if="scope.row.status === 2">
                  <el-tag> 已执行 </el-tag>
                </span>
                <span v-else>
                  <el-tag type="danger"> 未知 </el-tag>
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="result" label="结果"> </el-table-column>
            <el-table-column prop="report" label="报告">
              <template slot-scope="scope">
                <el-button type="text" size="mini" @click="openReport(scope.row)">{{scope.row.report}}</el-button>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template slot-scope="scope">
              <el-button type="success" size="mini" @click="runCase(scope.row)" @click.stop="drawer = false">执行</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <el-drawer
        title="报告"
        :visible.sync="drawer"
        direction="rtl"
        size="40%">
        <span>
          <el-tabs v-model="activeName" style="margin-left: 5px; margin-right: 5px;">
            <el-tab-pane label="System Out" name="first">
              <el-input
                type="textarea"
                :rows="25"
                placeholder="system out is null"
                v-model="caseInfo.system_out">
              </el-input>
            </el-tab-pane>
            <el-tab-pane label="Error" name="second">
              <el-input
                type="textarea"
                :rows="25"
                placeholder="error info null"
                v-model="caseInfo.error">
              </el-input>
            </el-tab-pane>
          </el-tabs>
        </span>
      </el-drawer>
    </el-card>
  </div>
</template>

<script>
import ProjectApi from '../../request/project'
import CaseApi from '../../request/case'

export default {
  name: 'case',
  components: {
    // 组件
  },
  data() {
    return {
      loading: true,
      projectId: '',
      caseNumber: 0,
      fileData: [],
      caseData: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      projectOptions: [],
      drawer: false,
      activeName: 'first',
      caseInfo: ''
    }
  },

  mounted() {
    // 初始化方法
    this.initProjectList()
  },

  methods: {
    // 获取项目列表
    async initProjectList() {
      this.loading = true
      const resp = await ProjectApi.getProjects()
      if (resp.success === true) {
        for (let i = 0; i < resp.data.length; i++) {
          this.projectOptions.push({
            value: resp.data[i].id,
            label: resp.data[i].name
          })
        }
        this.projectId = this.projectOptions[0].value
        this.initProjectFile()
      } else {
        this.$message.error(resp.error.message)
      }
      this.loading = false
    },

    // 初始化项目文件列表
    async initProjectFile() {
      const resp = await ProjectApi.getProjectTree(this.projectId)
      if (resp.success === true) {
        this.fileData = resp.data.files
        this.caseNumber = resp.data.case_number
      } else {
        this.$message.error(resp.error.message)
      }
    },

    // 点击项目文件
    handleNodeClick(data) {
      // 如果是文件返回 类&方法
      if (data.label.match('.py')) {
        ProjectApi.getProjectCases(this.projectId, data.full_name).then(resp => {
          if (resp.success === true) {
            this.$message.success('获取用例成功')
            this.caseData = resp.data
          } else {
            this.$message.error(resp.error.message)
          }
        })
      } else {
        // 如果目录返回下一级 目录&文件
        if (data.children.length > 0) {
          // 下一级不为空，直接返回
          return
        }
        ProjectApi.getProjectSubdirectory(this.projectId, data.full_name).then(resp => {
          if (resp.success === true) {
            this.$message.success('获取用例成功')
            data.children = resp.data
          } else {
            this.$message.error(resp.error.message)
          }
        })
      }
    },

    // 同步项目用例
    async syncProject() {
      if (this.projectId === '') {
        this.$message.error('请选择项目')
        return
      }
      const resp = await ProjectApi.syncProjectCase(this.projectId)
      if (resp.success === true) {
        this.initProjectFile()
        this.$message.success('同步成功')
      } else {
        this.$message.error(resp.error.message)
      }
    },

    changeProject() {
      this.initProjectFile()
    },

    // 运行用例
    async runCase(row) {
      const resp = await CaseApi.runningCase(row.id)
      if (resp.success === true) {
        this.$message.success('开始执行')
      } else {
        this.$message.error('运行失败')
      }
    },

    // 打开报告
    openReport(row) {
      window.open('/reports/' + row.report)
    },

    caseRowClick(row) {
      this.caseInfo = row
      this.drawer = true
    }

  }
}
</script>

<style>
.el-popover.home-popover {
  width: 70px;
  min-width: auto;
}
</style>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
/* 定义当前组件使用的CSS */
</style>
