<!--
/**
* @author huzhiheng
* @date 2022-02-11
* @desc 首页/我的工作台
*/
-->
<template>
  <div class="workbench">
    <div style="padding-bottom: 20px; height: 30px;">
      <span class="span-left">
        <span class="page-title">项目管理</span>
      </span>
      <span class="span-breadcrumb">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>工作台</el-breadcrumb-item>
        </el-breadcrumb>
      </span>
    </div>
    <el-card class="main-card" shadow="never">
      <div class="filter-line">
        <el-button cy-data="create-project" type="primary" @click="showCreate()">创建</el-button>
      </div>
      <el-row>
        <div v-for="(item, index) in tableData" :key="index">
          <el-col :span="7" class="project-card">
            <el-card class="box-card">
              <div>
                <el-avatar shape="square" :size="100" fit="fill" :src="url"></el-avatar>
              </div>
              <div style="margin-top: 10px;">
                <el-tag>{{item.address}}</el-tag>
              </div>
              <div slot="header" class="clearfix">
                <span>{{item.id}} - {{item.name}} </span>
                <span style="float: right; padding: 3px 0">
                  <el-dropdown style="left: 5px;">
                    <i class="el-icon-setting" style="margin-right: 15px"></i>
                    <el-dropdown-menu slot="dropdown">
                      <el-dropdown-item>
                        <el-button cy-data="edit-project" @click="showEdit(item.id)" type="text" size="mini">编辑</el-button>
                      </el-dropdown-item>
                      <el-dropdown-item>
                        <el-button cy-data="delete-project" @click="deleteProject(item.id)" type="text">删除</el-button>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </el-dropdown>
                </span>
              </div>
              <div>
                {{item.describe}}
              </div>
            </el-card>
          </el-col>
        </div>
      </el-row>
    </el-card>

    <project-dialog v-if="showDailog" :pid=projectId @cancel="cancelProject"></project-dialog>
  </div>
</template>

<script>
import ProjectApi from '../../request/project'
import projectDialog from './projectDialog'

export default {
  name: 'Workbench',
  components: {
    // 组件
    projectDialog
  },
  data() {
    return {
      loading: false,
      showDailog: false,
      projectId: 0,
      tableData: [],
      url: 'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg'
    }
  },

  mounted() {
    // 初始化方法
    this.initProjects()
  },

  methods: {
    // 定义方法
    async initProjects() {
      this.loading = true
      const resp = await ProjectApi.getProjects()
      if (resp.success === true) {
        this.tableData = resp.data
        console.log('tadfasd', this.tableData)
      } else {
        this.$message.error(resp.error.message)
      }
      this.loading = false
    },
    // 显示创建窗口
    showCreate() {
      this.showDailog = true
    },
    // 显示编辑窗口
    showEdit(pid) {
      this.projectId = pid
      this.showDailog = true
    },
    // 子组件的回调
    cancelProject() {
      this.showDailog = false
      this.projectId = 0
      this.initProjects()
    },
    // 删除一条项目信息
    async deleteProject(pid) {
      const resp = await ProjectApi.deleteProject(pid)
      if (resp.success === true) {
        this.$message.success('删除成功！')
        this.initProjects()
      } else {
        this.$message.error('删除失败');
      }
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
.filter-line {
  height: 50px;
  text-align: left;
}
.foot-page {
  margin-top: 20px;
    float: right;
    margin-bottom: 20px;
}
.project-card {
  margin-left: 15px;
  margin-right: 15px;
  margin-top: 15px;
  margin-bottom: 15px
}
</style>
