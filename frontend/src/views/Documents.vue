<template>
  <div class="documents-page">
    <!-- Toolbar -->
    <el-card class="toolbar-card" shadow="never">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" :icon="Upload" @click="uploadDialogVisible = true">
            Upload Document
          </el-button>
          <el-button
            type="danger"
            :icon="Delete"
            :disabled="selectedIds.length === 0"
            @click="handleBatchDelete"
          >
            Batch Delete ({{ selectedIds.length }})
          </el-button>
        </div>

        <div class="toolbar-right">
          <el-select
            v-model="queryParams.category"
            placeholder="Select Category"
            clearable
            style="width: 140px"
            @change="fetchDocuments"
          >
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>

          <el-select
            v-model="queryParams.time_range"
            placeholder="Time Range"
            clearable
            style="width: 120px"
            @change="fetchDocuments"
          >
            <el-option label="Today" value="today" />
            <el-option label="Last 7 days" value="7days" />
            <el-option label="Last 30 days" value="30days" />
          </el-select>

          <el-button :icon="Refresh" circle @click="fetchDocuments" />
        </div>
      </div>
    </el-card>

    <!-- Document List -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="documents"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="Title" min-width="200">
          <template #default="{ row }">
            <div class="doc-title">{{ row.title }}</div>
            <div class="doc-summary">{{ row.summary }}</div>
          </template>
        </el-table-column>

        <el-table-column label="Category" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.category" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Source" width="120">
          <template #default="{ row }">
            <el-text size="small">{{ row.source }}</el-text>
          </template>
        </el-table-column>

        <el-table-column label="Tags" width="180">
          <template #default="{ row }">
            <el-tag
              v-for="tag in row.tags.slice(0, 2)"
              :key="tag"
              size="small"
              style="margin-right: 4px"
            >
              {{ tag }}
            </el-tag>
            <el-tag v-if="row.tags.length > 2" size="small">
              +{{ row.tags.length - 2 }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Created Time" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              text
              type="primary"
              size="small"
              :icon="View"
              @click="handleView(row)"
            >
              View
            </el-button>
            <el-button
              text
              type="primary"
              size="small"
              :icon="Edit"
              @click="handleEdit(row)"
            >
              Edit
            </el-button>
            <el-button
              text
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(row.id)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.per_page"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="fetchDocuments"
          @size-change="fetchDocuments"
        />
      </div>
    </el-card>

    <!-- Upload Dialog -->
    <el-dialog v-model="uploadDialogVisible" title="Upload Document" width="500px">
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="Category">
          <el-select
            v-model="uploadForm.category"
            placeholder="Select category"
            allow-create
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="File">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".pdf,.docx,.txt,.xlsx,.xls,.md"
          >
            <template #trigger>
              <el-button type="primary">Select File</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                Supports PDF, DOCX, TXT, Excel, Markdown formats. Max file size: 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadDialogVisible = false">Cancel</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          @click="handleUpload"
        >
          Upload
        </el-button>
      </template>
    </el-dialog>

    <!-- View Dialog -->
    <el-dialog v-model="viewDialogVisible" title="Document Details" width="700px">
      <el-descriptions v-if="currentDoc" :column="2" border>
        <el-descriptions-item label="Title" :span="2">
          {{ currentDoc.title }}
        </el-descriptions-item>
        <el-descriptions-item label="Category">
          {{ currentDoc.category }}
        </el-descriptions-item>
        <el-descriptions-item label="Source">
          {{ currentDoc.source }}
        </el-descriptions-item>
        <el-descriptions-item label="Tags" :span="2">
          <el-tag
            v-for="tag in currentDoc.tags"
            :key="tag"
            style="margin-right: 8px"
          >
            {{ tag }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Created" :span="2">
          {{ formatDate(currentDoc.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="Content" :span="2">
          <div class="doc-content">{{ currentDoc.content }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Edit Dialog -->
    <el-dialog v-model="editDialogVisible" title="Edit Document" width="600px">
      <el-form v-if="editForm" :model="editForm" label-width="80px">
        <el-form-item label="Title">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select
            v-model="editForm.category"
            placeholder="Select category"
            allow-create
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Tags">
          <el-select
            v-model="editForm.tags"
            multiple
            filterable
            allow-create
            placeholder="Enter tags"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input
            v-model="editForm.notes"
            type="textarea"
            :rows="4"
            placeholder="Enter notes"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleUpdate">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Delete, Refresh, View, Edit } from '@element-plus/icons-vue'
import { documentAPI } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const uploading = ref(false)
const documents = ref([])
const total = ref(0)
const selectedIds = ref([])
const categories = ref([])

const queryParams = reactive({
  page: 1,
  per_page: 20,
  category: '',
  time_range: ''
})

const uploadDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const editDialogVisible = ref(false)

const uploadForm = reactive({
  category: '',
  file: null
})

const currentDoc = ref(null)
const editForm = ref(null)
const uploadRef = ref()

// Format date
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// Fetch document list
const fetchDocuments = async () => {
  loading.value = true
  try {
    const res = await documentAPI.getDocuments(queryParams)
    documents.value = res.documents
    total.value = res.total
  } catch (error) {
    console.error('Failed to fetch documents:', error)
  } finally {
    loading.value = false
  }
}

// Fetch category list
const fetchCategories = async () => {
  try {
    const res = await documentAPI.getCategories()
    categories.value = res.categories
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

// Selection change
const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map((item) => item.id)
}

// File selection
const handleFileChange = (file) => {
  uploadForm.file = file.raw
}

// Upload document
const handleUpload = async () => {
  if (!uploadForm.file) {
    ElMessage.warning('Please select a file')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('category', uploadForm.category || 'Uncategorized')

    await documentAPI.uploadDocument(formData)
    ElMessage.success('Upload successful')
    uploadDialogVisible.value = false
    uploadForm.category = ''
    uploadForm.file = null
    uploadRef.value?.clearFiles()
    fetchDocuments()
    fetchCategories()
  } catch (error) {
    console.error('Upload failed:', error)
  } finally {
    uploading.value = false
  }
}

// View document
const handleView = async (row) => {
  try {
    const res = await documentAPI.getDocument(row.id)
    currentDoc.value = res.document
    viewDialogVisible.value = true
  } catch (error) {
    console.error('Failed to fetch document:', error)
  }
}

// Edit document
const handleEdit = (row) => {
  editForm.value = {
    id: row.id,
    title: row.title,
    category: row.category,
    tags: row.tags || [],
    notes: row.notes || ''
  }
  editDialogVisible.value = true
}

// Update document
const handleUpdate = async () => {
  try {
    await documentAPI.updateDocument(editForm.value.id, {
      title: editForm.value.title,
      category: editForm.value.category,
      tags: editForm.value.tags,
      notes: editForm.value.notes
    })
    ElMessage.success('Update successful')
    editDialogVisible.value = false
    fetchDocuments()
  } catch (error) {
    console.error('Update failed:', error)
  }
}

// Delete document
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this document?', 'Confirm', {
      confirmButtonText: 'Confirm',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })

    await documentAPI.deleteDocument(id)
    ElMessage.success('Delete successful')
    fetchDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
    }
  }
}

// Batch delete
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete ${selectedIds.value.length} selected documents?`,
      'Confirm',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    await documentAPI.batchDelete(selectedIds.value)
    ElMessage.success('Delete successful')
    selectedIds.value = []
    fetchDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Batch delete failed:', error)
    }
  }
}

onMounted(() => {
  // Delayed loading to ensure token is ready
  setTimeout(() => {
    fetchDocuments()
    fetchCategories()
  }, 300)
})
</script>

<style scoped>
.documents-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.toolbar-card {
  flex-shrink: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.table-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.doc-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.doc-summary {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.doc-content {
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>

