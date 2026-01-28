<template>
  <div class="environment-table">
    <el-table :data="data" v-loading="loading" style="width: 100%">
      <el-table-column prop="name" :label="$t('apiTesting.component.environmentTable.environmentName')" min-width="200" />
      <el-table-column prop="scope" :label="$t('apiTesting.component.environmentTable.scope')" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.scope === 'GLOBAL' ? 'primary' : 'success'">
            {{ scope.row.scope === 'GLOBAL' ? $t('apiTesting.component.environmentTable.global') : $t('apiTesting.component.environmentTable.local') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="scope === 'LOCAL'" prop="project_name" :label="$t('apiTesting.component.environmentTable.relatedProject')" width="150" />
      <el-table-column :label="$t('apiTesting.component.environmentTable.variableCount')" width="100">
        <template #default="scope">
          {{ Object.keys(scope.row.variables || {}).length }}
        </template>
      </el-table-column>
      <el-table-column prop="is_active" :label="$t('apiTesting.component.environmentTable.status')" width="80">
        <template #default="scope">
          <el-tag v-if="scope.row.is_active" type="success" size="small">{{ $t('apiTesting.component.environmentTable.activated') }}</el-tag>
          <el-tag v-else type="info" size="small">{{ $t('apiTesting.component.environmentTable.notActivated') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_by.username" :label="$t('apiTesting.component.environmentTable.createdBy')" width="120" />
      <el-table-column prop="created_at" :label="$t('apiTesting.component.environmentTable.createdAt')" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('apiTesting.component.environmentTable.operation')" width="250" fixed="right">
        <template #default="scope">
          <el-button-group>
            <el-button
              v-if="!scope.row.is_active"
              link
              type="success"
              @click="$emit('activate', scope.row)"
              size="small"
            >
              {{ $t('apiTesting.component.environmentTable.activate') }}
            </el-button>
            <el-button link type="primary" @click="viewVariables(scope.row)" size="small">
              {{ $t('apiTesting.component.environmentTable.viewVariables') }}
            </el-button>
            <el-button link type="primary" @click="$emit('edit', scope.row)" size="small">
              {{ $t('apiTesting.component.environmentTable.edit') }}
            </el-button>
            <el-button link type="primary" @click="$emit('duplicate', scope.row)" size="small">
              {{ $t('apiTesting.component.environmentTable.copy') }}
            </el-button>
            <el-button link type="danger" @click="$emit('delete', scope.row)" size="small">
              {{ $t('apiTesting.component.environmentTable.delete') }}
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- 查看变量对话框 -->
    <el-dialog
      v-model="showViewDialog"
      :title="$t('apiTesting.component.environmentTable.environmentVariables')"
      width="600px"
    >
      <div v-if="viewingEnvironment" class="variables-view">
        <div class="env-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item :label="$t('apiTesting.component.environmentTable.environmentName')">
              {{ viewingEnvironment.name }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('apiTesting.component.environmentTable.scope')">
              <el-tag :type="viewingEnvironment.scope === 'GLOBAL' ? 'primary' : 'success'">
                {{ viewingEnvironment.scope === 'GLOBAL' ? $t('apiTesting.component.environmentTable.global') : $t('apiTesting.component.environmentTable.local') }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="viewingEnvironment.project_name" :label="$t('apiTesting.component.environmentTable.relatedProject')">
              {{ viewingEnvironment.project_name }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('apiTesting.component.environmentTable.status')">
              <el-tag v-if="viewingEnvironment.is_active" type="success">{{ $t('apiTesting.component.environmentTable.activated') }}</el-tag>
              <el-tag v-else type="info">{{ $t('apiTesting.component.environmentTable.notActivated') }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="variables-table">
          <h4>{{ $t('apiTesting.component.environmentTable.variableList') }}</h4>
          <el-table :data="formatVariables(viewingEnvironment.variables)" style="width: 100%">
            <el-table-column prop="key" :label="$t('apiTesting.component.environmentTable.variableName')" width="150" />
            <el-table-column prop="initialValue" :label="$t('apiTesting.component.environmentTable.initialValue')" />
            <el-table-column prop="currentValue" :label="$t('apiTesting.component.environmentTable.currentValue')" />
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button @click="showViewDialog = false">{{ $t('apiTesting.component.environmentTable.close') }}</el-button>
        <el-button type="primary" @click="$emit('edit', viewingEnvironment)">
          {{ $t('apiTesting.component.environmentTable.editEnvironment') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import dayjs from 'dayjs'

defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  scope: {
    type: String,
    default: 'GLOBAL'
  }
})

defineEmits(['edit', 'delete', 'activate', 'duplicate'])

const showViewDialog = ref(false)
const viewingEnvironment = ref(null)

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const formatVariables = (variables) => {
  if (!variables || typeof variables !== 'object') return []
  
  return Object.keys(variables).map(key => {
    const value = variables[key]
    if (typeof value === 'object') {
      return {
        key,
        initialValue: value.initialValue || '',
        currentValue: value.currentValue || value.initialValue || ''
      }
    } else {
      return {
        key,
        initialValue: value || '',
        currentValue: value || ''
      }
    }
  })
}

const viewVariables = (environment) => {
  viewingEnvironment.value = environment
  showViewDialog.value = true
}
</script>

<style scoped>
.environment-table {
  height: 100%;
}

.variables-view {
  max-height: 70vh;
  overflow-y: auto;
}

.env-info {
  margin-bottom: 20px;
}

.variables-table h4 {
  margin: 20px 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}
</style>