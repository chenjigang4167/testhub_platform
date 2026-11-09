<template>
  <div class="interface-management">
    <div class="interface-layout">
      <!-- 左侧集合树 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <el-select v-model="selectedProject" :placeholder="$t('apiTesting.common.selectProject')" @change="onProjectChange" style="width: 100%;">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              :placeholder="$t('apiTesting.interface.searchInterface')"
              size="small"
              clearable
              @input="onSearchDebounced"
              @keyup.enter="onSearch(searchKeyword)"
              style="flex: 1; min-width: 0;"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" size="small" @click="openCreateCollectionDialog" :title="$t('apiTesting.interface.createCollection')">
              <el-icon><Folder /></el-icon>
            </el-button>
            <el-button type="success" size="small" @click="createEmptyRequest" :title="$t('apiTesting.interface.addInterface')">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="collection-tree" v-show="!searchKeyword || searchKeyword.trim() === ''">
          <el-tree
            ref="treeRef"
            :data="collections"
            :props="treeProps"
            node-key="id"
            :expand-on-click-node="false"
            :default-expanded-keys="expandedKeys"
            draggable
            :allow-drag="allowDrag"
            :allow-drop="allowDrop"
            @node-click="onNodeClick"
            @node-contextmenu="onNodeRightClick"
            @node-expand="onNodeExpand"
            @node-collapse="onNodeCollapse"
            @node-drop="handleDrop"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon v-if="data.type === 'collection'">
                  <Folder />
                </el-icon>
                <el-icon v-else>
                  <Document />
                </el-icon>

                <!-- 集合名称编辑 -->
                <div v-if="data.type === 'collection' && editingNodeId === data.id" class="node-edit">
                  <el-input
                    v-model="editingNodeName"
                    size="small"
                    @blur="saveCollectionName"
                    @keyup.enter="saveCollectionName"
                    @keyup.esc="cancelEdit"
                    ref="editInputRef"
                  />
                </div>

                <!-- 普通显示模式 -->
                <span v-else class="node-label" :title="node.label">{{ node.label }}</span>

                <span v-if="data.type === 'request' && data.request_type !== 'WEBSOCKET'" class="method-tag" :class="(data.method || 'GET').toLowerCase()">
                  {{ data.method || 'GET' }}
                </span>

                <!-- 悬浮操作按钮：复制（仅接口）、删除 -->
                <div class="node-actions" @click.stop>
                  <el-tooltip v-if="data.type === 'request'" :content="$t('apiTesting.interface.contextMenu.copy')" placement="top">
                    <el-button link size="small" :icon="CopyDocument" @click.stop="copyRequest(data)" />
                  </el-tooltip>
                  <el-tooltip :content="$t('apiTesting.interface.contextMenu.delete')" placement="top">
                    <el-button link size="small" :icon="Delete" @click.stop="deleteNode(data)" />
                  </el-tooltip>
                </div>
              </div>
            </template>
          </el-tree>

          <!-- 搜索结果 -->
          <div v-if="filteredCollections.length > 0" class="search-results">
            <div class="search-results-header">
              <span>{{ $t('apiTesting.interface.searchResults', { count: filteredCollections.length }) }}</span>
              <el-button size="small" text @click="clearSearch">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <div class="search-results-list">
              <div
                v-for="item in filteredCollections"
                :key="item.id"
                class="search-result-item"
                @click="selectSearchResult(item)"
              >
                <el-icon><Document /></el-icon>
                <div class="search-result-content">
                  <div class="search-result-name">{{ item.name }}</div>
                  <div class="search-result-url">{{ item.url }}</div>
                </div>
                <el-tag v-if="item.matchType === 'name'" type="primary" size="small">{{ $t('apiTesting.interface.name') }}</el-tag>
                <el-tag v-else-if="item.matchType === 'method'" type="warning" size="small">{{ $t('apiTesting.interface.method') }}</el-tag>
                <el-tag v-else type="success" size="small">{{ $t('apiTesting.interface.url') }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧请求详情 -->
      <div class="main-content">
        <div v-if="!selectedRequest" class="empty-state">
          <el-empty :description="$t('apiTesting.interface.selectInterface')">
            <el-button type="primary" @click="createEmptyRequest">{{ $t('apiTesting.interface.createNewInterface') }}</el-button>
          </el-empty>
        </div>

        <div v-else class="request-detail">
          <!-- 请求基本信息 -->
          <div class="request-header">
            <div class="request-line">
              <!-- HTTP接口显示方法选择器 -->
              <el-select
                v-model="requestMethod"
                class="method-select"
                :class="requestMethod.toLowerCase()"
                :placeholder="'GET'"
                :popper-class="'method-select-dropdown'"
              >
                <el-option
                  v-for="method in availableMethods"
                  :key="method"
                  :label="method"
                  :value="method"
                  :class="method.toLowerCase()"
                />
              </el-select>

              <el-input
                v-model="requestUrl"
                :placeholder="$t('apiTesting.interface.inputRequestUrl')"
                class="url-input"
              >
                <template #prepend>
                  <el-select v-model="selectedEnvironment" :placeholder="$t('apiTesting.interface.environment')" class="env-select">
                    <el-option :label="$t('apiTesting.common.noEnvironment')" :value="null" />
                    <el-option
                      v-for="env in environments"
                      :key="env.id"
                      :label="env.name"
                      :value="env.id"
                    />
                  </el-select>
                </template>
              </el-input>

              <!-- WebSocket连接按钮 -->
              <el-button
                v-if="selectedRequest && selectedRequest.request_type === 'WEBSOCKET'"
                :type="websocketConnectionStatus === 'disconnected' ? 'primary' : 'info'"
                :loading="websocketConnectionStatus === 'connecting'"
                @click="toggleWebSocketConnection"
                class="send-button"
              >
                <span v-if="websocketConnectionStatus === 'disconnected'">{{ $t('apiTesting.interface.connect') }}</span>
                <span v-else-if="websocketConnectionStatus === 'connecting'">{{ $t('apiTesting.interface.connecting') }}</span>
                <span v-else>{{ $t('apiTesting.interface.disconnect') }}</span>
              </el-button>

              <!-- HTTP发送按钮 -->
              <el-button
                v-if="!selectedRequest || !selectedRequest.request_type || selectedRequest.request_type !== 'WEBSOCKET'"
                type="primary"
                @click="sendRequest"
                :loading="sending"
                class="send-button"
              >
                {{ $t('apiTesting.interface.send') }}
              </el-button>
            </div>

            <div class="request-meta">
              <el-input
                v-model="selectedRequest.name"
                :placeholder="$t('apiTesting.interface.requestName')"
                size="small"
                class="name-input"
              />
              <div class="action-buttons">
                <el-button size="small" @click="saveRequest" :loading="saving" ref="saveButtonRef">
                  {{ $t('apiTesting.common.save') }}
                </el-button>
                <el-dropdown split-button type="default" size="small" @click="importCurl">
                  {{ $t('apiTesting.common.import') }}
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="importCurl">{{ $t('apiTesting.interface.importCurl') }}</el-dropdown-item>
                      <el-dropdown-item @click="exportRequest">{{ $t('apiTesting.interface.exportCurl') }}</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-dropdown split-button type="default" size="small" @click="generateCode('javascript')">
                  {{ $t('apiTesting.interface.generateCode') }}
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="generateCode('javascript')">JavaScript</el-dropdown-item>
                      <el-dropdown-item @click="generateCode('python')">Python</el-dropdown-item>
                      <el-dropdown-item @click="generateCode('java')">Java</el-dropdown-item>
                      <el-dropdown-item @click="generateCode('curl')">cURL</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>

          <!-- 请求配置 -->
          <el-tabs v-model="activeTab" class="request-tabs">
            <el-tab-pane label="Params" name="params">
              <KeyValueEditor
                v-model="selectedRequest.params"
                :placeholder-key="$t('apiTesting.interface.paramName')"
                :placeholder-value="$t('apiTesting.interface.paramValue')"
              />
            </el-tab-pane>

            <el-tab-pane label="Headers" name="headers">
              <KeyValueEditor
                ref="headersEditorRef"
                v-model="selectedRequest.headers"
                :placeholder-key="$t('apiTesting.interface.headerName')"
                :placeholder-value="$t('apiTesting.interface.headerValue')"
                @update:modelValue="onHeadersUpdate"
              />
            </el-tab-pane>

            <el-tab-pane label="Body" name="body" v-if="hasBody">
              <div class="body-container">
                <el-radio-group v-model="bodyType" @change="onBodyTypeChange">
                  <el-radio value="none">none</el-radio>
                  <el-radio value="form-data">form-data</el-radio>
                  <el-radio value="x-www-form-urlencoded">x-www-form-urlencoded</el-radio>
                  <el-radio value="raw">raw</el-radio>
                  <el-radio value="binary">binary</el-radio>
                </el-radio-group>

                <div v-if="bodyType === 'form-data'" class="body-content">
                  <KeyValueEditor
                    v-model="formData"
                    :placeholder-key="$t('apiTesting.interface.key')"
                    :placeholder-value="$t('apiTesting.interface.value')"
                    :show-file="true"
                  />
                </div>

                <div v-else-if="bodyType === 'x-www-form-urlencoded'" class="body-content">
                  <KeyValueEditor
                    v-model="formUrlEncoded"
                    :placeholder-key="$t('apiTesting.interface.key')"
                    :placeholder-value="$t('apiTesting.interface.value')"
                  />
                </div>

                <div v-else-if="bodyType === 'raw'" class="body-content">
                  <div class="raw-options">
                    <el-select v-model="rawType" style="width: 150px;">
                      <el-option label="Text" value="text" />
                      <el-option label="JSON" value="json" />
                      <el-option label="HTML" value="html" />
                      <el-option label="XML" value="xml" />
                    </el-select>

                    <el-button
                      size="small"
                      :icon="MagicStick"
                      @click="openDataFactorySelectorForBody('rawBody')"
                      :title="$t('apiTesting.interface.referDataFactory')"
                      class="data-factory-btn"
                    >
                      {{ $t('apiTesting.interface.referDataFactory') }}
                    </el-button>
                    <el-button
                      size="small"
                      :icon="MagicStick"
                      @click="openVariableHelper('rawBody')"
                      :title="$t('apiTesting.interface.variableHelper')"
                      class="variable-helper-btn"
                    >
                      {{ $t('apiTesting.interface.variableHelper') }}
                    </el-button>
                  </div>
                  <el-input
                    ref="rawBodyInputRef"
                    v-model="rawBody"
                    type="textarea"
                    :rows="10"
                    :placeholder="$t('apiTesting.interface.inputRequestBody')"
                    class="raw-body"
                  />
                </div>
              </div>
            </el-tab-pane>

            <!-- HTTP接口专用标签页 -->
            <template v-if="!selectedRequest || selectedRequest.request_type !== 'WEBSOCKET'">
              <el-tab-pane label="Pre-request Script" name="pre-script">
                <div class="script-editor-container">
                  <el-input
                    v-model="selectedRequest.pre_request_script"
                    type="textarea"
                    :rows="10"
                    placeholder="// 请求前脚本，使用JavaScript语法"
                  />
                  <div class="script-buttons">
                    <el-button
                      size="small"
                      :icon="MagicStick"
                      @click="openDataFactorySelectorForScript('pre_request_script')"
                      :title="$t('apiTesting.interface.referDataFactory')"
                      class="script-factory-btn"
                    >
                      {{ $t('apiTesting.interface.referDataFactory') }}
                    </el-button>
                    <el-button
                      size="small"
                      :icon="MagicStick"
                      @click="openVariableHelper('pre_request_script')"
                      :title="$t('apiTesting.interface.variableHelper')"
                      class="script-variable-btn"
                    >
                      {{ $t('apiTesting.interface.variableHelper') }}
                    </el-button>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="Tests" name="tests">
                <div class="script-editor-container">
                  <el-input
                    v-model="selectedRequest.post_request_script"
                    type="textarea"
                    :rows="10"
                    placeholder="// 请求后脚本和测试，使用JavaScript语法"
                  />
                  <div class="script-buttons">
                    <el-button
                      size="small"
                      :icon="MagicStick"
                      @click="openDataFactorySelectorForScript('post_request_script')"
                      :title="$t('apiTesting.interface.referDataFactory')"
                      class="script-factory-btn"
                    >
                      {{ $t('apiTesting.interface.referDataFactory') }}
                    </el-button>
                    <el-button
                      size="small"
                      :icon="MagicStick"
                      @click="openVariableHelper('post_request_script')"
                      :title="$t('apiTesting.interface.variableHelper')"
                      class="script-variable-btn"
                    >
                      {{ $t('apiTesting.interface.variableHelper') }}
                    </el-button>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane :label="$t('apiTesting.interface.assertions')" name="assertions">
                <div class="assertions-editor">
                  <div class="assertions-header">
                    <el-button size="small" type="primary" @click="addAssertion">
                      <el-icon><Plus /></el-icon>
                      {{ $t('apiTesting.interface.addAssertion') }}
                    </el-button>
                  </div>

                  <div class="assertions-list">
                    <div
                      v-for="(assertion, index) in selectedRequest.assertions"
                      :key="index"
                      class="assertion-item"
                    >
                      <div class="assertion-header">
                        <el-input
                          v-model="assertion.name"
                          :placeholder="$t('apiTesting.interface.assertionName')"
                          size="small"
                          class="assertion-name"
                        />
                        <el-button
                          size="small"
                          type="danger"
                          @click="removeAssertion(index)"
                          circle
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>

                      <div class="assertion-config">
                        <el-select
                          v-model="assertion.type"
                          :placeholder="$t('apiTesting.interface.selectAssertionType')"
                          size="small"
                          @change="onAssertionTypeChange(assertion)"
                        >
                          <el-option :label="$t('apiTesting.interface.assertionTypes.statusCode')" value="status_code" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.responseTime')" value="response_time" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.contains')" value="contains" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.jsonPath')" value="json_path" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.header')" value="header" />
                          <el-option :label="$t('apiTesting.interface.assertionTypes.equals')" value="equals" />
                        </el-select>

                        <div class="assertion-params" v-if="assertion.type">
                          <!-- 状态码断言 -->
                          <div v-if="assertion.type === 'status_code'">
                            <el-input-number
                              v-model="assertion.expected"
                              :min="100"
                              :max="599"
                              size="small"
                              :placeholder="$t('apiTesting.interface.expectedStatusCode')"
                            />
                          </div>

                          <!-- 响应时间断言 -->
                          <div v-else-if="assertion.type === 'response_time'">
                            <el-input-number
                              v-model="assertion.expected"
                              :min="1"
                              size="small"
                              :placeholder="$t('apiTesting.interface.maxResponseTime')"
                            />
                          </div>

                          <!-- 包含文本断言 -->
                          <div v-else-if="assertion.type === 'contains'">
                            <div style="display: flex; align-items: center; width: 100%">
                              <el-input
                                v-model="assertion.expected"
                                :placeholder="$t('apiTesting.interface.expectedContains')"
                                size="small"
                                style="flex: 1"
                              >
                                <template #append>
                                  <el-button
                                    size="small"
                                    :icon="MagicStick"
                                    @click="openDataFactorySelector(assertion, 'expected', index)"
                                    :title="$t('apiTesting.interface.referDataFactory')"
                                    class="data-factory-btn"
                                  />
                                </template>
                              </el-input>
                              <el-tooltip :content="$t('apiTesting.interface.insertDynamicVariable')" placement="top">
                                <el-button size="small" style="margin-left: 5px" @click="openVariableHelperForAssertion(assertion, 'expected', index)" class="variable-helper-btn">
                                  <el-icon><MagicStick /></el-icon>
                                </el-button>
                              </el-tooltip>
                            </div>
                          </div>

                          <!-- JSON路径断言 -->
                          <div v-else-if="assertion.type === 'json_path'">
                            <el-input
                              v-model="assertion.json_path"
                              :placeholder="$t('apiTesting.interface.jsonPathExample')"
                              size="small"
                              class="assertion-input"
                            />
                            <div style="display: flex; align-items: center; width: 100%">
                              <el-input
                                v-model="assertion.expected"
                                :placeholder="$t('apiTesting.interface.expectedValue')"
                                size="small"
                                style="flex: 1"
                              >
                                <template #append>
                                  <el-button
                                    size="small"
                                    :icon="MagicStick"
                                    @click="openDataFactorySelector(assertion, 'expected', index)"
                                    :title="$t('apiTesting.interface.referDataFactory')"
                                    class="data-factory-btn"
                                  />
                                </template>
                              </el-input>
                              <el-tooltip :content="$t('apiTesting.interface.insertDynamicVariable')" placement="top">
                                <el-button size="small" style="margin-left: 5px" @click="openVariableHelperForAssertion(assertion, 'expected', index)" class="variable-helper-btn">
                                  <el-icon><MagicStick /></el-icon>
                                </el-button>
                              </el-tooltip>
                            </div>
                          </div>

                          <!-- 响应头断言 -->
                          <div v-else-if="assertion.type === 'header'">
                            <el-input
                              v-model="assertion.header_name"
                              :placeholder="$t('apiTesting.interface.headerNameLabel')"
                              size="small"
                              class="assertion-input"
                            />
                            <div style="display: flex; align-items: center; width: 100%">
                              <el-input
                                v-model="assertion.expected_value"
                                :placeholder="$t('apiTesting.interface.expectedValue')"
                                size="small"
                                style="flex: 1"
                              >
                                <template #append>
                                  <el-button
                                    size="small"
                                    :icon="MagicStick"
                                    @click="openDataFactorySelector(assertion, 'expected_value', index)"
                                    :title="$t('apiTesting.interface.referDataFactory')"
                                    class="data-factory-btn"
                                  />
                                </template>
                              </el-input>
                              <el-tooltip :content="$t('apiTesting.interface.insertDynamicVariable')" placement="top">
                                <el-button size="small" style="margin-left: 5px" @click="openVariableHelperForAssertion(assertion, 'expected_value', index)" class="variable-helper-btn">
                                  <el-icon><MagicStick /></el-icon>
                                </el-button>
                              </el-tooltip>
                            </div>
                          </div>

                          <!-- 完全匹配断言 -->
                          <div v-else-if="assertion.type === 'equals'">
                            <div style="display: flex; align-items: center; width: 100%">
                              <el-input
                                v-model="assertion.expected"
                                :placeholder="$t('apiTesting.interface.expectedMatch')"
                                size="small"
                                style="flex: 1"
                              >
                                <template #append>
                                  <el-button
                                    size="small"
                                    :icon="MagicStick"
                                    @click="openDataFactorySelector(assertion, 'expected', index)"
                                    :title="$t('apiTesting.interface.referDataFactory')"
                                    class="data-factory-btn"
                                  />
                                </template>
                              </el-input>
                              <el-tooltip :content="$t('apiTesting.interface.insertDynamicVariable')" placement="top">
                                <el-button size="small" style="margin-left: 5px" @click="openVariableHelperForAssertion(assertion, 'expected', index)" class="variable-helper-btn">
                                  <el-icon><MagicStick /></el-icon>
                                </el-button>
                              </el-tooltip>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div v-if="!selectedRequest.assertions || selectedRequest.assertions.length === 0" class="no-assertions">
                      <p>{{ $t('apiTesting.interface.noAssertions') }}</p>
                      <el-button size="small" type="primary" @click="addAssertion">
                        <el-icon><Plus /></el-icon>
                        {{ $t('apiTesting.interface.addFirstAssertion') }}
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane :label="$t('apiTesting.interface.extractVars')" name="extract">
                <div class="extract-editor">
                  <div class="extract-header">
                    <el-button size="small" type="primary" @click="addExtractRule">
                      <el-icon><Plus /></el-icon>
                      {{ $t('apiTesting.interface.addExtractRule') }}
                    </el-button>
                    <span class="extract-hint">{{ $t('apiTesting.interface.extractHint') }}</span>
                  </div>

                  <div v-if="extractRules.length" class="extract-table">
                    <div class="extract-row extract-row-head">
                      <span>{{ $t('apiTesting.interface.extractVarName') }}</span>
                      <span>{{ $t('apiTesting.interface.extractSource') }}</span>
                      <span>{{ $t('apiTesting.interface.extractPath') }}</span>
                      <span>{{ $t('apiTesting.interface.extractDefault') }}</span>
                      <span>{{ $t('apiTesting.interface.extractJoin') }}</span>
                      <span></span>
                    </div>
                    <div v-for="(rule, index) in extractRules" :key="index" class="extract-row">
                      <el-input
                        v-model="rule.name"
                        size="small"
                        :placeholder="$t('apiTesting.interface.extractVarNamePlaceholder')"
                      />
                      <el-select v-model="rule.source" size="small">
                        <el-option label="Body" value="body" />
                        <el-option label="Cookies" value="cookies" />
                        <el-option label="Headers" value="headers" />
                        <el-option label="Status Code" value="status_code" />
                      </el-select>
                      <el-input
                        v-model="rule.path"
                        size="small"
                        :disabled="rule.source === 'status_code'"
                        :placeholder="rule.source === 'status_code' ? '-' : $t('apiTesting.interface.extractPathPlaceholder')"
                      />
                      <el-input
                        v-model="rule.default"
                        size="small"
                        :placeholder="$t('apiTesting.interface.extractDefaultPlaceholder')"
                      />
                      <el-input
                        v-model="rule.join"
                        size="small"
                        :placeholder="$t('apiTesting.interface.extractJoinPlaceholder')"
                      />
                      <el-button link type="danger" size="small" @click="removeExtractRule(index)">
                        {{ $t('apiTesting.common.delete') }}
                      </el-button>
                    </div>
                  </div>

                  <div v-else class="no-assertions">
                    <p>{{ $t('apiTesting.interface.noExtractRules') }}</p>
                    <el-button size="small" type="primary" @click="addExtractRule">
                      <el-icon><Plus /></el-icon>
                      {{ $t('apiTesting.interface.addFirstExtractRule') }}
                    </el-button>
                  </div>
                </div>
              </el-tab-pane>
            </template>

            <!-- WebSocket接口专用标签页 -->
            <template v-else-if="selectedRequest && selectedRequest.request_type === 'WEBSOCKET'">
              <el-tab-pane label="Message" name="message">
                <div class="message-container">
                  <div class="message-input-section">
                    <el-select
                      v-model="websocketMessageType"
                      :placeholder="$t('apiTesting.interface.messageType')"
                      style="width: 150px; margin-bottom: 15px;"
                    >
                      <el-option label="Text" value="text" />
                      <el-option label="JSON" value="json" />
                      <el-option label="Binary" value="binary" />
                    </el-select>

                    <div v-if="websocketMessageType === 'text' || websocketMessageType === 'json'">
                      <el-input
                        v-model="websocketMessageContent"
                        type="textarea"
                        :rows="6"
                        :placeholder="$t('apiTesting.interface.inputWebSocketMessage')"
                      />
                    </div>

                    <div v-else-if="websocketMessageType === 'binary'">
                      <el-upload
                        drag
                        action="#"
                        :auto-upload="false"
                        :show-file-list="false"
                        :on-change="handleWebSocketFileUpload"
                      >
                        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                        <div class="el-upload__text">
                          {{ $t('apiTesting.interface.dragBinaryFile') }}<em>{{ $t('apiTesting.interface.clickUpload') }}</em>
                        </div>
                      </el-upload>
                      <div v-if="websocketBinaryFile" class="uploaded-file">
                        <span>{{ websocketBinaryFile.name }}</span>
                        <el-button size="small" type="danger" @click="clearWebSocketBinaryFile">{{ $t('apiTesting.interface.clear') }}</el-button>
                      </div>
                    </div>

                    <div class="message-actions" style="margin-top: 15px;">
                      <el-button type="primary" @click="sendWebSocketMessage">
                        {{ $t('apiTesting.interface.sendMessage') }}
                      </el-button>
                      <el-button @click="clearWebSocketMessage">
                        {{ $t('apiTesting.interface.clearMessage') }}
                      </el-button>
                    </div>
                  </div>

                  <!-- WebSocket消息历史记录 -->
                  <div class="websocket-response-section" v-if="websocketMessages.length > 0">
                    <h3>{{ $t('apiTesting.interface.messageHistory') }}</h3>
                    <div class="websocket-messages">
                      <div
                        v-for="(msg, index) in websocketMessages.slice().reverse()"
                        :key="index"
                        class="websocket-message-item"
                        :class="msg.type"
                      >
                        <div class="message-header">
                          <span class="message-type" :class="msg.type">
                            {{ msg.type === 'sent' ? $t('apiTesting.interface.messageSent') :
                               msg.type === 'connected' ? $t('apiTesting.interface.messageConnected') :
                               msg.type === 'info' ? $t('apiTesting.interface.messageInfo') :
                               msg.type === 'error' ? $t('apiTesting.interface.messageError') : $t('apiTesting.interface.messageReceived') }}
                          </span>
                          <span class="message-time">{{ msg.timestamp }}</span>
                        </div>
                        <div class="message-content">
                          <pre v-if="msg.type === 'received' && isJsonString(msg.content)">{{ formatJson(msg.content) }}</pre>
                          <pre v-else>{{ msg.content }}</pre>
                        </div>
                      </div>
                    </div>
                    <div class="message-actions">
                      <el-button size="small" @click="clearWebSocketMessages">{{ $t('apiTesting.interface.clearHistory') }}</el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </template>
          </el-tabs>

          <!-- 响应区域 -->
          <div v-if="response" class="response-section">
            <div class="response-header">
              <h3>{{ $t('apiTesting.interface.response') }}</h3>
              <div class="response-info">
                <el-tag :type="getStatusType(response.status_code)">
                  {{ response.status_code }}
                </el-tag>
                <span class="response-time">{{ response.response_time ? response.response_time.toFixed(0) : 0 }}ms</span>
              </div>
            </div>

            <el-tabs v-model="resultActiveTab" class="result-tabs">
              <!-- 一级 tab：响应信息 -->
              <el-tab-pane :label="$t('apiTesting.interface.response')" name="response">
                <el-tabs v-model="responseActiveTab" class="nested-tabs">
                  <el-tab-pane label="Body" name="body">
                    <div class="response-body">
                      <div class="response-actions">
                        <el-button-group>
                          <el-button size="small" @click="formatResponse">{{ $t('apiTesting.interface.format') }}</el-button>
                          <el-button size="small" @click="copyResponse">{{ $t('apiTesting.interface.copy') }}</el-button>
                          <el-button size="small" @click="toggleJsonPathExtractor">
                            {{ $t('apiTesting.interface.jsonPathExtract') }}
                          </el-button>
                        </el-button-group>
                      </div>
                      <div v-if="showJsonPathExtractor" class="jsonpath-extractor">
                        <div class="jsonpath-input">
                          <el-input
                            v-model="jsonPathExpression"
                            :placeholder="$t('apiTesting.interface.jsonPathExample')"
                            size="small"
                            @input="evaluateJsonPath"
                          >
                            <template #append>
                              <el-button size="small" @click="copyJsonPathResult">{{ $t('apiTesting.interface.copyResult') }}</el-button>
                            </template>
                          </el-input>
                        </div>
                        <div v-if="jsonPathResult !== null" class="jsonpath-result">
                          <strong>{{ $t('apiTesting.interface.extractResult') }}</strong>
                          <pre>{{ jsonPathResult }}</pre>
                        </div>
                      </div>
                      <div class="response-content" v-html="highlightedResponseBody"></div>
                    </div>
                  </el-tab-pane>

                  <el-tab-pane label="Headers" name="headers">
                    <div class="response-headers">
                      <div v-for="(value, key) in (response.response_data?.headers || {})" :key="key" class="header-row">
                        <strong>{{ key }}:</strong> {{ value }}
                      </div>
                    </div>
                  </el-tab-pane>

                  <el-tab-pane :label="$t('apiTesting.interface.assertionResults')" name="assertions" v-if="response.assertions_results && response.assertions_results.length > 0">
                    <div class="assertions-results">
                      <div
                        v-for="(result, index) in response.assertions_results"
                        :key="index"
                        class="assertion-result-item"
                        :class="{ 'passed': result.passed, 'failed': !result.passed }"
                      >
                        <div class="assertion-result-header">
                          <el-tag :type="result.passed ? 'success' : 'danger'" size="small">
                            {{ result.passed ? $t('apiTesting.interface.passed') : $t('apiTesting.interface.failed') }}
                          </el-tag>
                          <span class="assertion-name">{{ result.name }}</span>
                        </div>
                        <div class="assertion-result-details">
                          <div class="result-row">
                            <span class="label">{{ $t('apiTesting.interface.expected') }}</span>
                            <span class="value">{{ formatAssertionValue(result.expected) }}</span>
                          </div>
                          <div class="result-row">
                            <span class="label">{{ $t('apiTesting.interface.actual') }}</span>
                            <span class="value">{{ formatAssertionValue(result.actual) }}</span>
                          </div>
                          <div class="result-row" v-if="result.error">
                            <span class="label">{{ $t('apiTesting.interface.error') }}</span>
                            <span class="value error">{{ result.error }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </el-tab-pane>

                  <el-tab-pane
                    :label="$t('apiTesting.interface.extractResults')"
                    name="extract"
                    v-if="response.extract_results && response.extract_results.length > 0"
                  >
                    <div class="extract-results">
                      <div
                        v-for="(item, index) in response.extract_results"
                        :key="index"
                        class="assertion-result-item"
                        :class="{ 'passed': item.success, 'failed': !item.success }"
                      >
                        <div class="assertion-result-header">
                          <el-tag :type="item.success ? 'success' : 'danger'" size="small">
                            {{ item.success ? $t('apiTesting.interface.extracted') : $t('apiTesting.interface.failed') }}
                          </el-tag>
                          <span class="assertion-name">{{ item.name }}</span>
                        </div>
                        <div class="assertion-result-details">
                          <div class="result-row">
                            <span class="label">{{ $t('apiTesting.interface.extractValue') }}</span>
                            <span class="value">{{ item.success ? String(item.value) : $t('apiTesting.interface.notObtained') }}</span>
                          </div>
                          <div class="result-row" v-if="item.error">
                            <span class="label">{{ $t('apiTesting.interface.error') }}</span>
                            <span class="value error">{{ item.error }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>

              <!-- 一级 tab：请求信息 -->
              <el-tab-pane :label="$t('apiTesting.interface.requestInfo')" name="request">
                <div class="header-row request-line">
                  <strong>{{ response.request_data?.method }}</strong>
                  <span class="request-url">{{ response.request_data?.url }}</span>
                </div>
                <el-tabs v-model="requestActiveTab" class="nested-tabs">
                  <el-tab-pane label="Body" name="body">
                    <div v-if="hasRequestBodyData" class="response-content">{{ formattedRequestBody }}</div>
                    <div v-else class="empty-tip">{{ $t('apiTesting.interface.noRequestBody') }}</div>
                  </el-tab-pane>

                  <el-tab-pane label="Headers" name="headers">
                    <div v-if="Object.keys(response.request_data?.headers || {}).length > 0" class="response-headers">
                      <div v-for="(value, key) in (response.request_data?.headers || {})" :key="key" class="header-row">
                        <strong>{{ key }}:</strong> {{ value }}
                      </div>
                    </div>
                    <div v-else class="empty-tip">{{ $t('apiTesting.interface.noRequestHeaders') }}</div>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建集合对话框 -->
    <el-dialog v-model="showCreateCollectionDialog" :title="$t('apiTesting.interface.createCollection')" :close-on-click-modal="false" :close-on-press-escape="false" :modal="true" :destroy-on-close="false" width="500px">
      <el-form ref="collectionFormRef" :model="collectionForm" :rules="collectionRules" label-width="100px">
        <el-form-item :label="$t('apiTesting.interface.collectionName')" prop="name">
          <el-input v-model="collectionForm.name" :placeholder="$t('apiTesting.interface.inputCollectionName')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.common.description')" prop="description">
          <el-input v-model="collectionForm.description" type="textarea" :rows="3" :placeholder="`${$t('apiTesting.common.pleaseInput')}${$t('apiTesting.common.description')}`" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.interface.parentCollection')" prop="parent">
          <el-select v-model="collectionForm.parent" :placeholder="$t('apiTesting.interface.selectParentCollection')" clearable>
            <el-option
              v-for="collection in flatCollections"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="closeCreateCollectionDialog">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="createCollection">{{ $t('apiTesting.common.create') }}</el-button>
      </template>
    </el-dialog>

    <!-- 编辑集合对话框 -->
    <el-dialog v-model="showEditCollectionDialog" :title="$t('apiTesting.interface.editCollection')" :close-on-click-modal="false" width="500px">
      <el-form ref="editCollectionFormRef" :model="editCollectionForm" :rules="collectionRules" label-width="100px">
        <el-form-item :label="$t('apiTesting.interface.collectionName')" prop="name">
          <el-input v-model="editCollectionForm.name" :placeholder="$t('apiTesting.interface.inputCollectionName')" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.common.description')" prop="description">
          <el-input v-model="editCollectionForm.description" type="textarea" :rows="3" :placeholder="`${$t('apiTesting.common.pleaseInput')}${$t('apiTesting.common.description')}`" />
        </el-form-item>
        <el-form-item :label="$t('apiTesting.interface.parentCollection')" prop="parent">
          <el-select v-model="editCollectionForm.parent" :placeholder="$t('apiTesting.interface.selectParentCollection')" clearable>
            <el-option
              v-for="collection in flatCollections.filter(c => c.id !== editCollectionForm.id)"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="closeEditCollectionDialog">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="editCollection">{{ $t('apiTesting.common.save') }}</el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <ul v-show="showContextMenu" class="context-menu" :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }">
      <li @click="addRequest">{{ $t('apiTesting.interface.contextMenu.addRequest') }}</li>
      <li @click="addCollection">{{ $t('apiTesting.interface.contextMenu.addSubCollection') }}</li>
      <li @click="editNode">{{ $t('apiTesting.interface.contextMenu.edit') }}</li>
      <li @click="deleteNode">{{ $t('apiTesting.interface.contextMenu.delete') }}</li>
    </ul>

    <!-- 数据工厂选择器 -->
    <DataFactorySelector
      v-model="showDataFactorySelector"
      @select="handleDataFactorySelect"
    />

    <!-- 变量助手对话框 -->
    <el-dialog
      :close-on-press-escape="false"
      :modal="true"
      :destroy-on-close="false"
      v-model="showVariableHelper"
      :title="$t('apiTesting.interface.variableHelper') + ' (点击插入)'"
      :close-on-click-modal="false"
      width="900px"
    >
      <div v-if="variableCategories.length === 0" style="padding: 20px; text-align: center; color: #999;">
        <p>{{ $t('apiTesting.interface.variableCategoriesLoading') }}</p>
        <p>{{ $t('apiTesting.interface.variableCategoriesCount', { count: variableCategories.length }) }}</p>
      </div>
      <el-tabs v-else tab-position="left" style="height: 450px">
        <el-tab-pane
          v-for="(category, index) in variableCategories"
          :key="index"
          :label="category.label"
        >
          <div style="height: 450px; overflow-y: auto; padding: 10px;">
            <el-table :data="category.variables" style="width: 100%" @row-click="insertVariable" highlight-current-row>
              <el-table-column prop="name" :label="$t('apiTesting.interface.functionName')" width="150">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="desc" :label="$t('apiTesting.interface.description')" min-width="150" />
              <el-table-column prop="syntax" :label="$t('apiTesting.interface.syntax')" min-width="200" show-overflow-tooltip />
              <el-table-column prop="example" :label="$t('apiTesting.interface.example')" min-width="200" show-overflow-tooltip />
              <el-table-column :label="$t('apiTesting.interface.operation')" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" size="small">{{ $t('apiTesting.interface.insert') }}</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- CURL导入对话框 -->
    <el-dialog
      v-model="showCurlImportDialog"
      :title="$t('apiTesting.interface.importCurlCommand')"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-input
        v-model="curlCommand"
        type="textarea"
        :rows="15"
        :placeholder="$t('apiTesting.interface.pasteCurlCommand')"
      />
      <template #footer>
        <el-button @click="closeCurlImportDialog">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="parseAndImportCurl">{{ $t('apiTesting.interface.parseAndImport') }}</el-button>
      </template>
    </el-dialog>

    <!-- 代码生成对话框 -->
    <el-dialog
      v-model="showCodeGenerateDialog"
      :title="$t('apiTesting.interface.generateCode')"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-select v-model="codeLanguage" :placeholder="$t('apiTesting.interface.selectLanguage')" style="width: 150px; margin-bottom: 10px" @change="generateCode(codeLanguage)">
        <el-option label="JavaScript" value="javascript" />
        <el-option label="Python" value="python" />
        <el-option label="Java" value="java" />
        <el-option label="Node.js" value="node" />
        <el-option label="cURL" value="curl" />
        <el-option label="PHP" value="php" />
        <el-option label="Go" value="go" />
        <el-option label="C#" value="csharp" />
        <el-option label="Ruby" value="ruby" />
        <el-option label="Swift" value="swift" />
        <el-option label="Kotlin" value="kotlin" />
        <el-option label="Rust" value="rust" />
        <el-option label="Dart" value="dart" />
        <el-option label="Objective-C" value="objc" />
        <el-option label="PowerShell" value="powershell" />
        <el-option label="MATLAB" value="matlab" />
        <el-option label="R" value="r" />
        <el-option label="Ansible" value="ansible" />
        <el-option label="C" value="c" />
        <el-option label="CFML" value="cfml" />
        <el-option label="Clojure" value="clojure" />
        <el-option label="Elixir" value="elixir" />
        <el-option label="HTTP" value="http" />
        <el-option label="HTTPie" value="httpie" />
        <el-option label="Julia" value="julia" />
        <el-option label="Lua" value="lua" />
        <el-option label="OCaml" value="ocaml" />
        <el-option label="Perl" value="perl" />
        <el-option label="Wget" value="wget" />
      </el-select>
      <el-input
        v-model="generatedCode"
        type="textarea"
        :rows="20"
        readonly
        class="code-generate"
      />
      <template #footer>
        <el-button @click="closeCodeGenerateDialog">{{ $t('apiTesting.common.cancel') }}</el-button>
        <el-button type="primary" @click="copyGeneratedCode">{{ $t('apiTesting.common.copy') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Folder, Document, MagicStick, Search, Close, CopyDocument, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'
import KeyValueEditor from './components/KeyValueEditor.vue'
import DataFactorySelector from '@/components/DataFactorySelector.vue'
import { RequestModelParser } from '@/utils/requestModel'
import { getVariableFunctions } from '@/api/data-factory'
import { CodeGenerator } from '@/utils/codeGenerator'
import { debounce } from 'lodash-es'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const treeRef = ref(null)
const expandedKeys = ref([])
const projects = ref([])
const selectedProject = ref(null)
const collections = ref([])
const flatCollections = ref([])
const environments = ref([])
const selectedEnvironment = ref(null)
const selectedRequest = ref(null)
const response = ref(null)
const sending = ref(false)
const saving = ref(false)
const activeTab = ref('params')
const resultActiveTab = ref('response')
const responseActiveTab = ref('body')
const requestActiveTab = ref('body')
const showCreateCollectionDialog = ref(false)
const showEditCollectionDialog = ref(false)
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const rightClickedNode = ref(null)
const headersEditorRef = ref(null)
const editingNodeId = ref(null)
const editingNodeName = ref('')
const editInputRef = ref(null)
const rawBodyInputRef = ref(null)
const currentHeaders = ref({})

const searchKeyword = ref('')
const filteredCollections = ref([])

const treeProps = {
  children: 'children',
  label: 'name'
}

// 数据工厂选择器相关
const showDataFactorySelector = ref(false)
const showVariableHelper = ref(false)
const currentEditingField = ref('')
const currentBodyField = ref('')
const currentAssertion = ref(null)
const currentAssertionField = ref('')
const currentAssertionIndex = ref(-1)
const currentScriptField = ref('')
const variableCategories = ref([])
const loading = ref(false)

// CURL导入相关
const showCurlImportDialog = ref(false)
const curlCommand = ref('')

// 代码生成相关
const showCodeGenerateDialog = ref(false)
const codeLanguage = ref('javascript')
const generatedCode = ref('')

// WebSocket相关
const websocketConnectionStatus = ref('disconnected') // disconnected, connecting, connected
const websocketConnection = ref(null)
const websocketMessages = ref([]) // WebSocket消息历史记录
const websocketMessageType = ref('text')
const websocketMessageContent = ref('')
const websocketBinaryFile = ref(null)

// JSONPath提取相关
const showJsonPathExtractor = ref(false)
const jsonPathExpression = ref('')
const jsonPathResult = ref(null)

// Body相关
const bodyType = ref('none')
const rawType = ref('text')
const formData = ref([])
const formUrlEncoded = ref([])
const rawBody = ref('')

const availableMethods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'CONNECT', 'TRACE']

const onSearchDebounced = debounce((value) => {
  onSearch(value)
}, 300)

const onSearch = async (value) => {
  if (!value || value.trim() === '') {
    filteredCollections.value = []
    return
  }

  try {
    const response = await api.get('/api-testing/collections/search', {
      params: {
        project: selectedProject.value,
        keyword: value
      }
    })
    // 后端可能返回分页格式 { results: [...] } 或直接返回数组
    filteredCollections.value = response.data.results || response.data || []
  } catch (error) {
    ElMessage.error('搜索失败')
    console.error('搜索失败:', error)
  }
}

const selectSearchResult = (item) => {
  selectedRequest.value = item
  searchKeyword.value = ''
  filteredCollections.value = []
}

const onProjectChange = async (projectId) => {
  if (!projectId) return

  try {
    await loadCollections(projectId)
    await loadEnvironments(projectId)
  } catch (error) {
    ElMessage.error('切换项目失败')
    console.error('切换项目失败:', error)
  }
}

const loadProjects = async () => {
  try {
    const response = await api.get('/api-testing/projects/')
    // 后端可能返回分页格式 { results: [...] } 或直接返回数组
    projects.value = response.data.results || response.data || []
    if (projects.value.length > 0) {
      selectedProject.value = projects.value[0].id
      await loadCollections(selectedProject.value)
      await loadEnvironments(selectedProject.value)
    }
  } catch (error) {
    ElMessage.error('加载项目失败')
    console.error('加载项目失败:', error)
  }
}

const loadCollections = async (projectId) => {
  try {
    const response = await api.get('/api-testing/collections/', {
      params: {
        project: projectId
      }
    })
    // 后端可能返回分页格式 { results: [...] } 或直接返回数组
    const collectionsData = response.data.results || response.data || []

    // 构建树形结构
    collections.value = buildTree(collectionsData)
    flatCollections.value = collectionsData

    // 加载请求
    await loadRequests()
  } catch (error) {
    ElMessage.error('加载集合失败')
    console.error('加载集合失败:', error)
  }
}

const loadEnvironments = async (projectId) => {
  try {
    // 不传递 project 参数，让后端返回所有可访问的环境（全局 + 当前用户项目），
    // 否则 DjangoFilterBackend 的 project 过滤会把 project 为 null 的全局环境过滤掉。
    const response = await api.get('/api-testing/environments/', {})
    // 后端可能返回分页格式 { results: [...] } 或直接返回数组
    const allEnvironments = response.data.results || response.data || []
    // 过滤出全局环境 + 当前项目的局部环境
    environments.value = allEnvironments.filter(env =>
      env.scope === 'GLOBAL' ||
      (env.scope === 'LOCAL' && (!projectId || env.project === projectId))
    )
  } catch (error) {
    ElMessage.error('加载环境失败')
    console.error('加载环境失败:', error)
  }
}

const buildTree = (items) => {
  const map = {}
  const roots = []

  items.forEach(item => {
    map[item.id] = {
      ...item,
      type: 'collection',
      children: []
    }
  })

  items.forEach(item => {
    if (item.parent) {
      if (map[item.parent]) {
        map[item.parent].children.push(map[item.id])
      }
    } else {
      roots.push(map[item.id])
    }
  })

  return roots
}

const findCollectionById = (collections, id) => {
  for (const collection of collections) {
    if (collection.id === id) return collection
    if (collection.children) {
      const found = findCollectionById(collection.children, id)
      if (found) return found
    }
  }
  return null
}

const clearCollectionChildren = (collection) => {
  if (collection.children) {
    collection.children = collection.children.filter(child => child.type === 'collection')
    collection.children.forEach(child => clearCollectionChildren(child))
  }
}

const loadRequests = async () => {
  if (!selectedProject.value) return

  try {
    const response = await api.get('/api-testing/requests/')
    const requests = response.data.results || response.data || []

    // 清空所有集合的子节点（请求）
    collections.value.forEach(collection => {
      clearCollectionChildren(collection)
    })

    // 过滤掉之前的未分类接口（type 为 request 且 id 为 null 的项）
    collections.value = collections.value.filter(item => item.type === 'collection')

    // 将请求添加到对应集合中或直接添加到根级别
    requests.forEach(request => {
      if (request.collection) {
        // 有关联集合的请求，添加到对应集合下
        const collection = findCollectionById(collections.value, request.collection)
        if (collection) {
          if (!collection.children) collection.children = []
          collection.children.push({
            ...request,
            type: 'request',
            name: request.name
          })
        }
      } else {
        // 未关联集合的请求，直接添加到集合列表的根级别
        collections.value.push({
          ...request,
          type: 'request',
          name: request.name
        })
      }
    })
  } catch (error) {
    ElMessage.error('加载请求失败')
    console.error('加载请求失败:', error)
  }
}

const flattenCollections = (items, parent = null) => {
  let result = []
  for (const item of items) {
    if (item.type === 'collection') {
      result.push(item)
      if (item.children && item.children.length > 0) {
        result = result.concat(flattenCollections(item.children, item))
      }
    }
  }
  return result
}

const onNodeClick = async (data) => {
  if (data.type === 'request') {
    try {
      const apiResponse = await api.get(`/api-testing/requests/${data.id}/`)
      const requestData = apiResponse.data

      // 初始化currentHeaders
      currentHeaders.value = requestData.headers || {}

      // 将 params 从字典格式转换为数组格式
      if (requestData.params && typeof requestData.params === 'object' && !Array.isArray(requestData.params)) {
        const paramsArray = []
        Object.keys(requestData.params).forEach(key => {
          if (key && requestData.params[key] !== undefined) {
            paramsArray.push({
              enabled: true,
              key,
              value: requestData.params[key],
              description: '',
              type: 'text'
            })
          }
        })
        requestData.params = paramsArray
      }

      // 将 headers 从字典格式转换为数组格式
      if (requestData.headers && typeof requestData.headers === 'object' && !Array.isArray(requestData.headers)) {
        const headersArray = []
        Object.keys(requestData.headers).forEach(key => {
          if (key && requestData.headers[key] !== undefined) {
            headersArray.push({
              enabled: true,
              key,
              value: requestData.headers[key],
              description: '',
              type: 'text'
            })
          }
        })
        requestData.headers = headersArray
      }

      // 解析body数据
      if (requestData.body && requestData.body.type) {
        if (requestData.body.type === 'json' && requestData.body.data) {
          bodyType.value = 'raw'
          rawType.value = 'json'
          rawBody.value = JSON.stringify(requestData.body.data, null, 2)
        } else if (requestData.body.type === 'raw' && requestData.body.data) {
          bodyType.value = 'raw'
          rawType.value = 'text'
          rawBody.value = requestData.body.data
        } else if (requestData.body.type === 'form-data') {
          bodyType.value = 'form-data'
          formData.value = requestData.body.data || []
        } else if (requestData.body.type === 'x-www-form-urlencoded') {
          bodyType.value = 'x-www-form-urlencoded'
          formUrlEncoded.value = requestData.body.data || []
        } else if (requestData.body.type === 'binary') {
          bodyType.value = 'binary'
        } else {
          bodyType.value = 'none'
          rawBody.value = ''
        }
      } else {
        bodyType.value = 'none'
        rawBody.value = ''
      }

      response.value = null
      selectedRequest.value = requestData
    } catch (error) {
      ElMessage.error('加载请求失败')
      console.error('加载请求失败:', error)
    }
  }
}

const onNodeRightClick = (event, node, treeNode) => {
  event.preventDefault()
  showContextMenu.value = true
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  rightClickedNode.value = node
}

const onNodeExpand = (node) => {
  expandedKeys.value.push(node.id)
}

const onNodeCollapse = (node) => {
  expandedKeys.value = expandedKeys.value.filter(key => key !== node.id)
}

const createEmptyRequest = () => {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  const newRequest = {
    id: null,
    collection: null,
    name: '未命名接口',
    url: '',
    method: 'GET',
    params: {},
    headers: {},
    pre_request_script: '',
    post_request_script: '',
    assertions: [],
    extract_rules: [],
    request_type: 'HTTP'
  }

  selectedRequest.value = newRequest
}

const openCreateCollectionDialog = () => {
  showCreateCollectionDialog.value = true
}

const clearSearch = () => {
  searchKeyword.value = ''
  filteredCollections.value = []
}

const closeCreateCollectionDialog = () => {
  showCreateCollectionDialog.value = false
}

const closeEditCollectionDialog = () => {
  showEditCollectionDialog.value = false
}

const closeCurlImportDialog = () => {
  showCurlImportDialog.value = false
}

const closeCodeGenerateDialog = () => {
  showCodeGenerateDialog.value = false
}

const toggleJsonPathExtractor = () => {
  showJsonPathExtractor.value = !showJsonPathExtractor.value
}

const addRequest = () => {
  if (!rightClickedNode.value) return

  const parentNode = rightClickedNode.value
  if (!parentNode || parentNode.type !== 'collection') {
    ElMessage.warning('只能在集合下添加接口')
    return
  }

  const newRequest = {
    id: null,
    collection: parentNode.id,
    name: '未命名接口',
    url: '',
    method: 'GET',
    params: {},
    headers: {},
    pre_request_script: '',
    post_request_script: '',
    assertions: [],
    extract_rules: [],
    request_type: 'HTTP'
  }

  selectedRequest.value = newRequest
  showContextMenu.value = false
}

const addCollection = () => {
  if (!rightClickedNode.value) return

  const parentNode = rightClickedNode.value
  if (!parentNode || parentNode.type !== 'collection') {
    ElMessage.warning('只能在集合下添加子集合')
    return
  }

  collectionForm.parent = parentNode.id
  showCreateCollectionDialog.value = true
  showContextMenu.value = false
}

const editNode = () => {
  if (!rightClickedNode.value) return

  const node = rightClickedNode.value
  if (!node) {
    ElMessage.warning('无法编辑此节点')
    return
  }

  if (node.type === 'collection') {
    editingNodeId.value = node.id
    editingNodeName.value = node.name
    showContextMenu.value = false

    nextTick(() => {
      editInputRef.value?.focus()
    })
  } else {
    ElMessage.warning('只能编辑集合名称')
  }
}

const deleteNode = (node = rightClickedNode.value) => {
  if (!node) {
    ElMessage.warning('无法删除此节点')
    return
  }

  const nodeName = node.name

  ElMessageBox.confirm(
    `确定要删除${node.type === 'collection' ? '集合' : '接口'}「${nodeName}」吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      if (node.type === 'collection') {
        await api.delete(`/api-testing/collections/${node.id}/`)
      } else {
        await api.delete(`/api-testing/requests/${node.id}/`)
      }
      ElMessage.success('删除成功')
      await loadCollections(selectedProject.value)
      showContextMenu.value = false
    } catch (error) {
      ElMessage.error('删除失败')
      console.error('删除失败:', error)
    }
  }).catch(() => {
    // 取消删除
    showContextMenu.value = false
  })
}

const copyRequest = async (node) => {
  if (!node || node.type !== 'request') return
  try {
    const { data } = await api.get(`/api-testing/requests/${node.id}/`)
    const payload = { ...data }
    delete payload.id
    delete payload.created_at
    delete payload.updated_at
    delete payload.created_by
    payload.name = `${data.name} (副本)`
    // collection 保持原值 → 复制到同一集合下
    await api.post('/api-testing/requests/', payload)
    ElMessage.success('复制成功')
    await loadCollections(selectedProject.value)
  } catch (error) {
    ElMessage.error('复制失败')
    console.error('复制失败:', error)
  }
}

// 仅接口节点可拖拽（集合不可拖，避免改动集合树结构）
const allowDrag = (node) => node.data.type === 'request'

// 仅允许把接口“放进”某个集合节点，不实现同集合内 prev/next 重排持久化
const allowDrop = (draggingNode, dropNode, type) =>
  type === 'inner' && dropNode?.data?.type === 'collection'

const handleDrop = async (draggingNode, dropNode) => {
  const requestId = draggingNode.data.id
  const targetCollectionId = dropNode.data.id
  // 同集合：el-tree 已乐观移动，统一 reload 回到服务端真实状态
  if (draggingNode.data.collection === targetCollectionId) {
    await loadCollections(selectedProject.value)
    return
  }
  try {
    await api.patch(`/api-testing/requests/${requestId}/`, { collection: targetCollectionId })
    ElMessage.success('已移动到目标集合')
  } catch (error) {
    ElMessage.error('移动失败')
    console.error('移动失败:', error)
  } finally {
    // el-tree 已乐观改了本地 collections，无论成败都用服务端状态覆盖，避免脏数据
    await loadCollections(selectedProject.value)
  }
}

const saveCollectionName = async () => {
  if (!editingNodeId.value || !editingNodeName.value.trim()) {
    cancelEdit()
    return
  }

  try {
    await api.patch(`/api-testing/collections/${editingNodeId.value}/`, {
      name: editingNodeName.value.trim()
    })
    ElMessage.success('保存成功')
    await loadCollections(selectedProject.value)
  } catch (error) {
    ElMessage.error('保存失败')
    console.error('保存失败:', error)
  } finally {
    cancelEdit()
  }
}

const cancelEdit = () => {
  editingNodeId.value = null
  editingNodeName.value = ''
}

const collectionForm = reactive({
  name: '',
  description: '',
  parent: null
})

const editCollectionForm = reactive({
  id: null,
  name: '',
  description: '',
  parent: null
})

const collectionRules = {
  name: [{ required: true, message: '请输入集合名称', trigger: 'blur' }]
}

const methodClass = computed(() => {
  const method = selectedRequest.value?.method || 'GET'
  return `method-${method.toLowerCase()}`
})

const getMethodClass = (method) => {
  return method ? method.toLowerCase() : 'get'
}

const getMethodColor = (method) => {
  const colors = {
    'get': '#61affe',
    'post': '#49cc90',
    'put': '#fca130',
    'delete': '#f93e3e',
    'patch': '#50e3c2',
    'head': '#9013fe',
    'options': '#0ebeff',
    'connect': '#7f8c8d',
    'trace': '#e67e22'
  }
  return colors[(method || 'GET').toLowerCase()] || '#61affe'
}

const requestMethod = computed({
  get: () => selectedRequest.value?.method || 'GET',
  set: (value) => {
    if (!selectedRequest.value) {
      // 如果selectedRequest为null，创建一个新的请求对象
      const newRequest = {
        method: value,
        url: '',
        type: 'request',
        request_type: 'HTTP',
        headers: [],
        params: [],
        body: {
          type: 'none',
          content: ''
        }
      }
      selectedRequest.value = newRequest
    } else {
      selectedRequest.value.method = value
    }
  }
})

const requestUrl = computed({
  get: () => selectedRequest.value?.url || '',
  set: (value) => {
    if (selectedRequest.value) {
      selectedRequest.value.url = value
    }
  }
})

const hasBody = computed(() => {
  return selectedRequest.value && selectedRequest.value.method && ['POST', 'PUT', 'PATCH'].includes(selectedRequest.value.method)
})

const responseBody = computed(() => {
  if (!response.value || !response.value.response_data) return ''

  try {
    if (response.value.response_data.json) {
      return JSON.stringify(response.value.response_data.json, null, 2)
    } else {
      return response.value.response_data.body || ''
    }
  } catch (e) {
    return response.value.response_data?.body || ''
  }
})

// 请求信息（执行后服务端返回的真实请求快照，已做变量解析）
const hasRequestBodyData = computed(() => {
  const body = response.value?.request_data?.body
  if (body === null || body === undefined || body === '') return false
  if (typeof body === 'object' && Object.keys(body).length === 0) return false
  return true
})

const formattedRequestBody = computed(() => {
  const body = response.value?.request_data?.body
  if (body === null || body === undefined || body === '') return ''
  if (typeof body === 'string') return body
  try {
    return JSON.stringify(body, null, 2)
  } catch (e) {
    return String(body)
  }
})

const convertKeyValueArrayToObject = (input) => {
  if (input && typeof input === 'object' && !Array.isArray(input)) {
    return input
  }

  if (!Array.isArray(input)) return {}

  const obj = {}
  input.forEach(item => {
    if (item.enabled !== false && item.key) {
      obj[item.key] = item.value || ''
    }
  })
  return obj
}

const highlightedResponseBody = computed(() => {
  if (!responseBody.value) return ''

  try {
    // 简单的 JSON 语法高亮
    return responseBody.value
      .replace(/"([^"]+)"\s*:/g, '<span style="color: #268bd2;">"$1"</span>:')
      .replace(/:\s*"([^"]+)"/g, ': <span style="color: #2aa198;">"$1"</span>')
      .replace(/:\s*(true|false|null)/g, ': <span style="color: #cb4b16;">$1</span>')
      .replace(/:\s*([0-9]+(\.[0-9]+)?)/g, ': <span style="color: #d33682;">$1</span>')
  } catch (e) {
    return responseBody.value
  }
})

const getStatusType = (status) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'warning'
  if (status >= 400) return 'danger'
  return 'info'
}

const sendRequest = async () => {
  if (!selectedRequest.value || !selectedRequest.value.url) {
    ElMessage.warning('请填写请求URL')
    return
  }

  try {
    sending.value = true

    // 发送请求前先自动保存当前的修改
    // await saveRequest()

    // 准备请求体数据
    let bodyData = {}
    if (hasBody.value) {
      if (bodyType.value === 'none') {
        bodyData = {}
      } else if (bodyType.value === 'raw' && rawBody.value) {
        if (rawType.value === 'json') {
          try {
            bodyData = {
              type: 'json',
              data: JSON.parse(rawBody.value)
            }
          } catch (e) {
            bodyData = {
              type: 'raw',
              data: rawBody.value
            }
          }
        } else {
          bodyData = {
            type: 'raw',
            data: rawBody.value
          }
        }
      } else if (bodyType.value === 'form-data') {
        bodyData = {
          type: 'form-data',
          data: formData.value || []
        }
      } else if (bodyType.value === 'x-www-form-urlencoded') {
        bodyData = {
          type: 'x-www-form-urlencoded',
          data: formUrlEncoded.value || []
        }
      } else if (bodyType.value === 'binary') {
        bodyData = {
          type: 'binary',
          data: null
        }
      }
    }

    const requestData = {
      url: selectedRequest.value.url,
      method: selectedRequest.value.method,
      params: convertKeyValueArrayToObject(selectedRequest.value.params || []),
      headers: selectedRequest.value.headers,
      extract_rules: buildExtractRules(),
      environment_id: selectedEnvironment.value
    }
    
    // 对于GET请求，不发送body字段
    if (hasBody.value) {
      requestData.body = bodyData
    }

    const apiResponse = await api.post(`/api-testing/requests/${selectedRequest.value.id}/execute/`, requestData)
    response.value = apiResponse.data

    ElMessage.success('请求成功')
  } catch (error) {
    ElMessage.error('请求失败')
    console.error('请求失败:', error)
  } finally {
    sending.value = false
  }
}

const onHeadersUpdate = (headers) => {
  if (selectedRequest.value) {
    currentHeaders.value = headers
    selectedRequest.value.headers = headers
  }
}

const saveRequest = async () => {
  if (!selectedRequest.value || !selectedRequest.value.url) {
    ElMessage.warning('请填写请求URL')
    return
  }

  try {
    saving.value = true

    // 准备保存的数据
    let bodyData = {}

    if (hasBody.value) {
      if (bodyType.value === 'none') {
        bodyData = {}
      } else if (bodyType.value === 'raw' && rawBody.value) {
        if (rawType.value === 'json') {
          try {
            bodyData = {
              type: 'json',
              data: JSON.parse(rawBody.value)
            }
          } catch (e) {
            bodyData = {
              type: 'raw',
              data: rawBody.value
            }
          }
        } else {
          bodyData = {
            type: 'raw',
            data: rawBody.value
          }
        }
      } else if (bodyType.value === 'form-data') {
        bodyData = {
          type: 'form-data',
          data: formData.value || []
        }
      } else if (bodyType.value === 'x-www-form-urlencoded') {
        bodyData = {
          type: 'x-www-form-urlencoded',
          data: formUrlEncoded.value || []
        }
      } else if (bodyType.value === 'binary') {
        bodyData = {
          type: 'binary',
          data: null
        }
      }
    }

    // 直接从KeyValueEditor组件获取当前headers（完整数组格式）
    let finalHeaders = []
    if (headersEditorRef.value) {
      const rows = headersEditorRef.value.rows || []
      finalHeaders = rows
        .filter(row => row.enabled && row.key && row.key.trim())
        .map(row => ({
          key: row.key.trim(),
          value: row.value || '',
          description: row.description || '',
          enabled: row.enabled !== false
        }))
    } else {
      if (selectedRequest.value.headers && Array.isArray(selectedRequest.value.headers)) {
        finalHeaders = selectedRequest.value.headers.filter(item => item.enabled && item.key)
      }
    }

    const requestData = {
      ...selectedRequest.value,
      params: Array.isArray(selectedRequest.value.params) ? convertKeyValueArrayToObject(selectedRequest.value.params || []) : selectedRequest.value.params,
      headers: finalHeaders,
      extract_rules: buildExtractRules()
    }
    
    // 对于GET请求，不包含body字段
    if (hasBody.value) {
      requestData.body = bodyData
    }

    let response
    if (selectedRequest.value.id) {
      response = await api.put(`/api-testing/requests/${selectedRequest.value.id}/`, requestData)
    } else {
      response = await api.post('/api-testing/requests/', requestData)
    }

    selectedRequest.value = response.data
    await loadCollections(selectedProject.value)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const onBodyTypeChange = () => {
  // 保存当前body数据到selectedRequest
  if (selectedRequest.value) {
    if (bodyType.value === 'raw' && rawBody.value) {
      if (rawType.value === 'json') {
        try {
          selectedRequest.value.body = {
            type: 'json',
            data: JSON.parse(rawBody.value)
          }
        } catch (e) {
          selectedRequest.value.body = {
            type: 'raw',
            data: rawBody.value
          }
        }
      } else {
        selectedRequest.value.body = {
          type: 'raw',
          data: rawBody.value
        }
      }
    } else if (bodyType.value === 'form-data') {
      selectedRequest.value.body = {
        type: 'form-data',
        data: formData.value || []
      }
    } else if (bodyType.value === 'x-www-form-urlencoded') {
      selectedRequest.value.body = {
        type: 'x-www-form-urlencoded',
        data: formUrlEncoded.value || []
      }
    } else if (bodyType.value === 'binary') {
      selectedRequest.value.body = {
        type: 'binary',
        data: null
      }
    } else {
      selectedRequest.value.body = {
        type: 'none',
        data: null
      }
    }
  }
}

const addAssertion = () => {
  if (!selectedRequest.value) return

  if (!selectedRequest.value.assertions) {
    selectedRequest.value.assertions = []
  }

  selectedRequest.value.assertions.push({
    name: `${t('apiTesting.interface.assertion')}${selectedRequest.value.assertions.length + 1}`,
    type: 'status_code',
    expected: 200
  })
}

const removeAssertion = (index) => {
  if (!selectedRequest.value || !selectedRequest.value.assertions) return

  selectedRequest.value.assertions.splice(index, 1)
}

// ===== 变量提取规则 =====
const extractRules = computed(() => selectedRequest.value?.extract_rules || [])

const addExtractRule = () => {
  if (!selectedRequest.value) return

  if (!Array.isArray(selectedRequest.value.extract_rules)) {
    selectedRequest.value.extract_rules = []
  }

  selectedRequest.value.extract_rules.push({
    name: '',
    source: 'body',
    path: '',
    default: '',
    join: ''
  })
}

const removeExtractRule = (index) => {
  if (!selectedRequest.value || !Array.isArray(selectedRequest.value.extract_rules)) return

  selectedRequest.value.extract_rules.splice(index, 1)
}

// 提交给后端前做清洗：丢掉没填变量名的空行，空字符串的 default/join 不下发
// （后端把 default 为空字符串当成有效兜底值，会把失败显示成成功）
const buildExtractRules = () => {
  const rules = selectedRequest.value?.extract_rules || []
  return rules
    .filter(rule => rule && String(rule.name || '').trim())
    .map(rule => {
      const item = {
        name: String(rule.name).trim(),
        source: rule.source || 'body',
        path: String(rule.path || '').trim()
      }
      if (rule.default !== undefined && rule.default !== null && String(rule.default) !== '') {
        item.default = rule.default
      }
      if (rule.join !== undefined && rule.join !== null && String(rule.join) !== '') {
        item.join = rule.join
      }
      return item
    })
}

const onAssertionTypeChange = (assertion) => {
  // 根据断言类型重置相关字段
  if (assertion.type === 'status_code') {
    assertion.expected = 200
  } else if (assertion.type === 'response_time') {
    assertion.expected = 1000
  } else if (assertion.type === 'contains') {
    assertion.expected = ''
  } else if (assertion.type === 'json_path') {
    assertion.json_path = ''
    assertion.expected = ''
  } else if (assertion.type === 'header') {
    assertion.header_name = ''
    assertion.expected_value = ''
  } else if (assertion.type === 'equals') {
    assertion.expected = ''
  }
}

const formatResponse = () => {
  if (!response.value || !response.value.response_data) return

  try {
    if (response.value.response_data.json) {
      response.value.response_data.json = JSON.parse(JSON.stringify(response.value.response_data.json))
    }
    ElMessage.success('格式化成功')
  } catch (e) {
    ElMessage.error('格式化失败')
  }
}

const copyResponse = () => {
  if (responseBody.value) {
    navigator.clipboard.writeText(responseBody.value)
    ElMessage.success('已复制到剪贴板')
  }
}

const evaluateJsonPath = () => {
  if (!response.value || !response.value.response_data || !response.value.response_data.json || !jsonPathExpression.value) {
    jsonPathResult.value = null
    return
  }

  try {
    // 简单的JSONPath实现
    const json = response.value.response_data.json
    let result = json

    // 解析JSONPath表达式
    const parts = jsonPathExpression.value.split('.').filter(p => p)

    for (const part of parts) {
      if (part === '$') {
        result = json
      } else if (part.includes('[')) {
        // 处理数组索引
        const [arrayName, indexStr] = part.split('[')
        const index = parseInt(indexStr.replace(']', ''))
        result = result[arrayName][index]
      } else {
        result = result[part]
      }
    }

    jsonPathResult.value = JSON.stringify(result, null, 2)
  } catch (e) {
    jsonPathResult.value = 'JSONPath表达式错误'
  }
}

const copyJsonPathResult = () => {
  if (jsonPathResult.value) {
    navigator.clipboard.writeText(jsonPathResult.value)
    ElMessage.success('已复制到剪贴板')
  }
}

const formatAssertionValue = (value) => {
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value, null, 2)
  }
  return value
}

const createCollection = async () => {
  if (!collectionForm.name.trim()) {
    ElMessage.warning('请输入集合名称')
    return
  }

  try {
    const response = await api.post('/api-testing/collections/', {
      ...collectionForm,
      project: selectedProject.value
    })
    ElMessage.success('创建成功')
    await loadCollections(selectedProject.value)
    showCreateCollectionDialog.value = false
    collectionForm.name = ''
    collectionForm.description = ''
    collectionForm.parent = null
  } catch (error) {
    ElMessage.error('创建失败')
    console.error('创建失败:', error)
  }
}

const updateCollection = async () => {
  if (!editCollectionForm.name.trim()) {
    ElMessage.warning('请输入集合名称')
    return
  }

  try {
    await api.patch(`/api-testing/collections/${editCollectionForm.id}/`, editCollectionForm)
    ElMessage.success('更新成功')
    await loadCollections(selectedProject.value)
    showEditCollectionDialog.value = false
  } catch (error) {
    ElMessage.error('更新失败')
    console.error('更新失败:', error)
  }
}

const importCurl = () => {
  // 清空上次的 curl 命令
  curlCommand.value = ''
  showCurlImportDialog.value = true
}

const parseAndImportCurl = async () => {
  if (!curlCommand.value.trim()) {
    ElMessage.warning('请输入CURL命令')
    return
  }

  try {
    const requestModel = await RequestModelParser.parseCurl(curlCommand.value)

    if (!selectedRequest.value) {
      createEmptyRequest()
    }

    // 回填基本字段
    selectedRequest.value.method = requestModel.method
    selectedRequest.value.url = requestModel.baseURL + requestModel.path
    selectedRequest.value.headers = requestModel.headers
    selectedRequest.value.params = requestModel.query

    // 回填 body 相关字段
    if (requestModel.body.mode !== 'none') {
      if (requestModel.body.mode === 'json') {
        bodyType.value = 'raw'
        rawType.value = 'json'
        rawBody.value = requestModel.body.json || ''
      } else if (requestModel.body.mode === 'raw') {
        bodyType.value = 'raw'
        rawType.value = 'text'
        rawBody.value = requestModel.body.raw || ''
      } else if (requestModel.body.mode === 'formdata') {
        bodyType.value = 'form-data'
        formData.value = requestModel.body.formdata || []
      } else if (requestModel.body.mode === 'urlencoded') {
        bodyType.value = 'x-www-form-urlencoded'
        formUrlEncoded.value = requestModel.body.urlencoded || []
      }
    }

    showCurlImportDialog.value = false
    ElMessage.success('导入成功')
  } catch (error) {
    ElMessage.error('解析CURL命令失败')
    console.error('解析CURL命令失败:', error)
  }
}

// 辅助函数：将对象格式转换为数组格式
const convertToArrayFormat = (data) => {
  if (!data) return []
  // 如果已经是数组格式，直接返回
  if (Array.isArray(data)) return data
  // 如果是对象格式，转换为数组格式
  if (typeof data === 'object') {
    return Object.entries(data).map(([key, value]) => ({
      key,
      value: typeof value === 'object' ? JSON.stringify(value) : String(value),
      enabled: true
    }))
  }
  return []
}

const exportRequest = () => {
  if (!selectedRequest.value) return

  try {
    let baseURL = ''
    let path = ''

    if (selectedRequest.value.url) {
      try {
        const url = new URL(selectedRequest.value.url)
        baseURL = `${url.protocol}//${url.host}`
        path = url.pathname
      } catch (error) {
        baseURL = selectedRequest.value.url
        path = ''
      }
    }

    const requestModel = {
      method: selectedRequest.value?.method || 'GET',
      baseURL: baseURL,
      path: path,
      query: convertToArrayFormat(selectedRequest.value?.params),
      headers: convertToArrayFormat(selectedRequest.value?.headers),
      body: {
        mode: 'none',
        raw: rawBody.value || ''
      },
      timeout: 30000
    }

    const curlCommand = RequestModelParser.toCurl(requestModel)
    navigator.clipboard.writeText(curlCommand)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('导出失败:', error)
  }
}

const generateCode = async (language) => {
  if (!selectedRequest.value) return

  if (!selectedRequest.value.url) {
    ElMessage.warning('请求URL不能为空')
    return
  }

  try {
    // 更新语言选择器的值
    codeLanguage.value = language

    // 构建完整的 requestModel 对象
    let bodyMode = 'none'

    if (bodyType.value === 'raw') {
      bodyMode = rawType.value === 'json' ? 'json' : 'raw'
    } else if (bodyType.value === 'form-data') {
      bodyMode = 'formdata'
    } else if (bodyType.value === 'x-www-form-urlencoded') {
      bodyMode = 'urlencoded'
    } else if (bodyType.value === 'binary') {
      bodyMode = 'binary'
    }

    // 解析 URL 获取 baseURL 和 path
    let baseURL = ''
    let path = ''
    try {
      const url = new URL(selectedRequest.value.url)
      baseURL = `${url.protocol}//${url.host}`
      path = url.pathname
    } catch (error) {
      // 如果 URL 解析失败，使用整个 URL 作为 path
      path = selectedRequest.value.url
    }

    // 构建完整的 requestModel 对象
    const requestModel = {
      method: selectedRequest.value.method || 'GET',
      baseURL: baseURL,
      path: path,
      query: Array.isArray(selectedRequest.value.params) ? selectedRequest.value.params : [],
      headers: Array.isArray(selectedRequest.value.headers) ? selectedRequest.value.headers : [],
      body: {
        mode: bodyMode,
        raw: rawBody.value,
        json: rawBody.value,
        formdata: formData.value,
        urlencoded: formUrlEncoded.value
      },
      timeout: 30000
    }

    const code = await CodeGenerator.generateCode(requestModel, language)
    generatedCode.value = code
    showCodeGenerateDialog.value = true
  } catch (error) {
    ElMessage.error('生成代码失败')
    console.error('生成代码失败:', error)
  }
}

const copyGeneratedCode = () => {
  if (generatedCode.value) {
    navigator.clipboard.writeText(generatedCode.value)
    ElMessage.success('已复制到剪贴板')
  }
}

const toggleWebSocketConnection = async () => {
  if (!selectedRequest.value || !selectedRequest.value.url) {
    ElMessage.warning('请填写WebSocket URL')
    return
  }

  if (websocketConnectionStatus.value === 'connected') {
    // 关闭连接
    if (websocketConnection.value) {
      websocketConnection.value.close()
      websocketConnection.value = null
    }
    websocketConnectionStatus.value = 'disconnected'
    ElMessage.success('WebSocket连接已关闭')
  } else {
    // 建立连接
    try {
      websocketConnectionStatus.value = 'connecting'
      const wsUrl = selectedRequest.value.url.replace('http://', 'ws://').replace('https://', 'wss://')

      websocketConnection.value = new WebSocket(wsUrl)

      websocketConnection.value.onopen = () => {
        websocketConnectionStatus.value = 'connected'
        ElMessage.success('WebSocket连接成功')
        websocketMessages.value.push({
          type: 'connected',
          content: 'WebSocket连接成功',
          timestamp: new Date().toLocaleString()
        })
      }

      websocketConnection.value.onmessage = (event) => {
        websocketMessages.value.push({
          type: 'received',
          content: event.data,
          timestamp: new Date().toLocaleString()
        })
      }

      websocketConnection.value.onclose = () => {
        websocketConnectionStatus.value = 'disconnected'
        websocketConnection.value = null
        websocketMessages.value.push({
          type: 'info',
          content: 'WebSocket连接已关闭',
          timestamp: new Date().toLocaleString()
        })
      }

      websocketConnection.value.onerror = (error) => {
        websocketConnectionStatus.value = 'disconnected'
        websocketConnection.value = null
        ElMessage.error('WebSocket连接失败')
        websocketMessages.value.push({
          type: 'error',
          content: `WebSocket连接失败: ${error.message}`,
          timestamp: new Date().toLocaleString()
        })
      }
    } catch (error) {
      websocketConnectionStatus.value = 'disconnected'
      ElMessage.error('WebSocket连接失败')
      console.error('WebSocket连接失败:', error)
    }
  }
}

const sendWebSocketMessage = () => {
  if (!websocketConnection.value || websocketConnectionStatus.value !== 'connected') {
    ElMessage.warning('请先建立WebSocket连接')
    return
  }

  if (websocketMessageType.value === 'binary' && !websocketBinaryFile.value) {
    ElMessage.warning('请选择要发送的二进制文件')
    return
  }

  try {
    let message = websocketMessageContent.value
    if (websocketMessageType.value === 'json') {

      message = JSON.parse(message)
    }

    websocketConnection.value.send(message)
    websocketMessages.value.push({
      type: 'sent',
      content: websocketMessageContent.value,
      timestamp: new Date().toLocaleString()
    })

    if (websocketMessageType.value !== 'binary') {
      websocketMessageContent.value = ''
    }
  } catch (error) {
    ElMessage.error('发送消息失败')
    console.error('发送消息失败:', error)
  }
}

const clearWebSocketMessage = () => {
  websocketMessageContent.value = ''
  websocketBinaryFile.value = null
}

const clearWebSocketMessages = () => {
  websocketMessages.value = []
}

const handleWebSocketFileUpload = (file) => {
  websocketBinaryFile.value = file.raw
}

const clearWebSocketBinaryFile = () => {
  websocketBinaryFile.value = null
}

const isJsonString = (str) => {
  try {
    JSON.parse(str)
    return true
  } catch (e) {
    return false
  }
}

const formatJson = (str) => {
  try {
    const obj = JSON.parse(str)
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return str
  }
}

const openDataFactorySelectorForBody = (field) => {
  currentBodyField.value = field
  currentAssertion.value = null
  currentAssertionField.value = ''
  currentAssertionIndex.value = -1
  currentScriptField.value = ''
  showDataFactorySelector.value = true
}

const openDataFactorySelectorForScript = (field) => {
  currentScriptField.value = field
  currentAssertion.value = null
  currentAssertionField.value = ''
  currentAssertionIndex.value = -1
  showDataFactorySelector.value = true
}

const openDataFactorySelector = (assertion, field, index) => {
  currentAssertion.value = assertion
  currentAssertionField.value = field
  currentAssertionIndex.value = index
  currentScriptField.value = ''
  showDataFactorySelector.value = true
}

const openVariableHelper = (field) => {
  currentEditingField.value = field
  currentAssertion.value = null
  currentAssertionField.value = ''
  currentAssertionIndex.value = -1
  showVariableHelper.value = true
}

const openVariableHelperForAssertion = (assertion, field, index) => {
  currentAssertion.value = assertion
  currentAssertionField.value = field
  currentAssertionIndex.value = index
  currentEditingField.value = ''
  showVariableHelper.value = true
}

const insertVariable = (variable) => {
  // 确保variable是对象（处理行点击事件）
  if (typeof variable === 'object' && variable !== null) {
    if (currentEditingField.value && selectedRequest.value) {
      const example = variable.example

      if (currentEditingField.value === 'rawBody') {
        // 在光标位置插入变量
        insertTextAtCursor(rawBodyInputRef, example)
      } else if (currentEditingField.value === 'pre_request_script') {
        // 对于脚本字段，暂时保持追加到末尾的行为
        // （如果需要光标插入，需要为脚本编辑器添加ref并实现类似逻辑）
        const currentValue = selectedRequest.value.pre_request_script || ''
        selectedRequest.value.pre_request_script = currentValue + example
      } else if (currentEditingField.value === 'post_request_script') {
        const currentValue = selectedRequest.value.post_request_script || ''
        selectedRequest.value.post_request_script = currentValue + example
      }

      ElMessage.success(`已插入变量: ${variable.name}`)
      showVariableHelper.value = false
    } else if (currentAssertion.value && currentAssertionField.value) {
      const example = variable.example
      const field = currentAssertionField.value

      const currentValue = currentAssertion.value[field] || ''
      if (!currentValue) {
        currentAssertion.value[field] = example
      } else {
        currentAssertion.value[field] = currentValue + example
      }

      ElMessage.success(`已插入变量: ${variable.name}`)
      showVariableHelper.value = false
    }
  }
}

const handleDataFactorySelect = (record) => {
  if (!record || !record.output_data) return

  let valueToSet = ''

  if (typeof record.output_data === 'string') {
    valueToSet = record.output_data
  } else if (record.output_data.result) {
    valueToSet = record.output_data.result
  } else if (record.output_data.output_data) {
    valueToSet = record.output_data.output_data
  } else if (typeof record.output_data === 'object') {

    const possibleResultFields = ['result', 'value', 'data', 'output', 'content']
    let foundResult = false
    for (const field of possibleResultFields) {
      if (record.output_data[field] !== undefined) {
        valueToSet = record.output_data[field]
        foundResult = true
        break
      }
    }
    // 如果没有找到可能的结果字段，将整个对象转为JSON字符串
    if (!foundResult) {
      valueToSet = JSON.stringify(record.output_data)
    }
  } else {
    valueToSet = JSON.stringify(record.output_data)
  }

  // 确保valueToSet是字符串类型
  if (typeof valueToSet !== 'string') {
    valueToSet = JSON.stringify(valueToSet)
  }

  // 如果是断言字段
  if (currentAssertion.value) {
    currentAssertion.value[currentAssertionField.value] = valueToSet
    ElMessage.success(`${t('apiTesting.interface.referencedToAssertion')}: ${record.tool_name}`)
  }
  // 如果是Body字段
  else if (currentBodyField.value) {
    if (currentBodyField.value === 'rawBody') {
      // 在光标位置插入文本
      insertTextAtCursor(rawBodyInputRef, valueToSet)
    }
    ElMessage.success(`已引用数据工厂数据到Body: ${record.tool_name}`)
  }
  // 如果是脚本字段
  else if (currentScriptField.value && selectedRequest.value) {
    // 将值插入到脚本中
    const insertText = `\n// 来自数据工厂: ${record.tool_name}\nconst ${record.tool_name.replace(/\s+/g, '_')} = ${JSON.stringify(valueToSet)}\n`
    const currentValue = selectedRequest.value[currentScriptField.value] || ''
    selectedRequest.value[currentScriptField.value] = currentValue + insertText
    ElMessage.success(`已引用数据工厂数据到脚本: ${record.tool_name}`)
  }

  showDataFactorySelector.value = false
}

// 在光标位置插入文本的辅助函数
const insertTextAtCursor = (inputRef, textToInsert) => {
  if (!inputRef.value) {
    // 如果没有找到ref，直接追加到末尾
    rawBody.value = rawBody.value + textToInsert
    return
  }

  // 获取textarea DOM元素
  const textarea = inputRef.value.$el?.querySelector('textarea')
  if (!textarea) {
    // 如果找不到textarea元素，直接追加到末尾
    rawBody.value = rawBody.value + textToInsert
    return
  }

  const startPos = textarea.selectionStart
  const endPos = textarea.selectionEnd
  const currentValue = rawBody.value

  // 在光标位置插入新文本
  const newValue =
    currentValue.substring(0, startPos) +
    textToInsert +
    currentValue.substring(endPos)

  rawBody.value = newValue

  // 恢复光标位置到插入文本的末尾
  nextTick(() => {
    const newCursorPos = startPos + textToInsert.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    textarea.focus()
  })
}

// 加载变量函数
const loadVariableFunctions = async () => {
  try {
    loading.value = true
    console.log('开始加载变量函数...')
    const apiResponse = await getVariableFunctions()
    console.log('变量函数响应:', apiResponse)
    console.log('变量函数响应.data:', apiResponse.data)
    
    // 更灵活地处理响应数据结构
    let functionsData = null
    
    // 检查不同可能的数据结构
    if (apiResponse && apiResponse.data) {
      if (Array.isArray(apiResponse.data)) {
        // 后端返回的是数组，直接使用
        functionsData = apiResponse.data
      } else if (apiResponse.data.functions) {
        // 如果data中有functions字段，使用它
        functionsData = apiResponse.data.functions
      } else if (typeof apiResponse.data === 'object') {
        // 如果data是对象但没有functions字段，假设整个对象就是按分类组织的函数
        functionsData = apiResponse.data
      }
    }
    
    if (functionsData) {
      const groupedFunctions = functionsData
      console.log('处理后的 groupedFunctions:', groupedFunctions)

      // 后端已经按分类分组了，直接转换为标签页所需的格式
      if (typeof groupedFunctions === 'object' && !Array.isArray(groupedFunctions)) {
        variableCategories.value = Object.entries(groupedFunctions).map(([label, variables]) => ({
          label,
          variables
        }))
      } else if (Array.isArray(groupedFunctions)) {
        // 如果是数组，按分类分组
        const grouped = {}
        
        // 创建分类名称映射表
        const categoryMapping = {
          '随机数': t('apiTesting.component.keyValueEditor.categories.randomNumber'),
          '测试数据': t('apiTesting.component.keyValueEditor.categories.testData'),
          '字符串': t('apiTesting.component.keyValueEditor.categories.string'),
          '编码转换': t('apiTesting.component.keyValueEditor.categories.encodingConversion'),
          '加密': t('apiTesting.component.keyValueEditor.categories.encryption'),
          '时间日期': t('apiTesting.component.keyValueEditor.categories.datetime'),
          'Crontab': t('apiTesting.component.keyValueEditor.categories.crontab'),
          '未分类': t('apiTesting.component.keyValueEditor.categories.uncategorized')
        }
        
        groupedFunctions.forEach(func => {
          const rawCategory = func.category || '未分类'
          // 使用映射表获取正确的分类名称
          const category = categoryMapping[rawCategory] || rawCategory
          if (!grouped[category]) {
            grouped[category] = []
          }
          grouped[category].push(func)
        })
        
        // 定义固定的分类顺序 ['随机数', '测试数据', '字符串', '编码转换', '加密', '时间日期', 'Crontab', '未分类']
        const categoryOrder = [
          t('apiTesting.component.keyValueEditor.categories.randomNumber'),
          t('apiTesting.component.keyValueEditor.categories.testData'),
          t('apiTesting.component.keyValueEditor.categories.string'),
          t('apiTesting.component.keyValueEditor.categories.encodingConversion'),
          t('apiTesting.component.keyValueEditor.categories.encryption'),
          t('apiTesting.component.keyValueEditor.categories.datetime'),
          t('apiTesting.component.keyValueEditor.categories.crontab'),
          t('apiTesting.component.keyValueEditor.categories.uncategorized')
        ]
        
        // 按固定顺序构建分类列表
        const orderedCategories = []
        categoryOrder.forEach(category => {
          if (grouped[category]) {
            orderedCategories.push({
              label: category,
              variables: grouped[category]
            })
            delete grouped[category]
          }
        })
        
        // 添加剩余的分类（如果有）
        Object.entries(grouped).forEach(([label, variables]) => {
          orderedCategories.push({
            label,
            variables
          })
        })
        
        variableCategories.value = orderedCategories
      }

      console.log('最终变量分类:', variableCategories.value)
    } else {
      console.error('响应数据格式错误，无法找到函数数据')
      console.error('完整响应:', apiResponse)
    }
  } catch (error) {
    console.error('加载变量函数失败:', error)
    ElMessage.error('加载变量函数失败，使用本地数据')
    // 加载失败时使用本地变量分类数据
    useLocalVariableCategories()
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(async () => {
  await loadProjects()
  await loadVariableFunctions()

  // 添加全局点击事件监听器，用于隐藏右键菜单
  document.addEventListener('click', handleGlobalClick)
  document.addEventListener('contextmenu', handleGlobalClick)
})

onBeforeUnmount(() => {
  // 移除全局点击事件监听器
  document.removeEventListener('click', handleGlobalClick)
  document.removeEventListener('contextmenu', handleGlobalClick)
})

// 处理全局点击事件，隐藏右键菜单
const handleGlobalClick = (event) => {
  // 当显示右键菜单时，点击任何地方（除了菜单本身）都应该隐藏菜单
  if (showContextMenu.value) {
    const contextMenu = document.querySelector('.context-menu')
    if (!contextMenu || !contextMenu.contains(event.target)) {
      showContextMenu.value = false
    }
  }
}

// 使用本地变量分类数据
const useLocalVariableCategories = () => {
  variableCategories.value = [
    {
      label: t('apiTesting.component.keyValueEditor.categories.randomNumber'),
      variables: [
        { name: 'random_int', syntax: '${random_int(min, max, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomInt'), example: '${random_int(100, 999, 1)}' },
        { name: 'random_float', syntax: '${random_float(min, max, precision, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomFloat'), example: '${random_float(0, 1, 2, 1)}' },
        { name: 'random_boolean', syntax: '${random_boolean(count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomBoolean'), example: '${random_boolean(1)}' },
        { name: 'random_date', syntax: '${random_date(start_date, end_date, count, date_format)}', desc: t('apiTesting.component.keyValueEditor.variables.randomDate'), example: '${random_date(2024-01-01, 2024-12-31, 1, %Y-%m-%d)}' }
      ]
    },
    {
      label: t('apiTesting.component.keyValueEditor.categories.randomString'),
      variables: [
        { name: 'random_string', syntax: '${random_string(length, char_type, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomString'), example: '${random_string(8, all, 1)}' },
        { name: 'random_uuid', syntax: '${random_uuid(version, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomUuid'), example: '${random_uuid(4, 1)}' },
        { name: 'random_mac_address', syntax: '${random_mac_address(separator, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomMacAddress'), example: '${random_mac_address(:, 1)}' },
        { name: 'random_ip_address', syntax: '${random_ip_address(ip_version, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomIpAddress'), example: '${random_ip_address(4, 1)}' },
        { name: 'random_sequence', syntax: '${random_sequence(sequence, count, unique)}', desc: t('apiTesting.component.keyValueEditor.variables.randomSequence'), example: '${random_sequence([a,b,c], 1, false)}' }
      ]
    }
  ]
  console.log('使用本地变量分类数据:', variableCategories.value)
}
</script>

<style scoped>
.interface-management {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.interface-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧边栏 */
.sidebar {
  width: 300px;
  border-right: 1px solid #e4e7ed;
  background: #ffffff;
  overflow: visible;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: stretch;
  position: relative;
  background: #f8f9fa;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.header-actions .el-input {
  flex: 1;
  min-width: 0;
}

.header-actions .el-button {
  border-radius: 6px;
  transition: all 0.2s ease;
}

.header-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.collection-tree {
  flex: 1;
  overflow: auto;
  padding: 10px;
  min-width: 0;
}

/* el-tree 节点内容行：打断 min-content 宽度向上传播，
   否则长接口名会让整行撑宽、把复制/删除按钮挤出可视区 */
.collection-tree :deep(.el-tree-node__content) {
  min-width: 0;
  overflow: hidden;
}

.collection-tree :deep(.el-tree-node__content > .el-tree-node__label) {
  display: none;
}

/* 树节点样式 */
.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  padding: 4px 0;
}

.tree-node .el-icon {
  font-size: 16px;
  color: #606266;
  flex-shrink: 0;
}

.node-label {
  flex: 1;
  min-width: 0;
  font-size: 14px;
  color: #303133;
  transition: color 0.2s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-node:hover .node-label {
  color: #409eff;
}

/* 悬浮操作按钮：默认隐藏，悬浮节点时显示 */
.node-actions {
  margin-left: auto;
  flex-shrink: 0;
  display: none;
  align-items: center;
  gap: 2px;
}

.tree-node:hover .node-actions {
  display: flex;
}

.node-actions .el-button {
  padding: 2px;
  color: #909399;
}

.node-actions .el-button:hover {
  color: #409eff;
}

.node-edit {
  flex: 1;
}

.node-edit .el-input {
  font-size: 14px;
}

/* 方法标签样式 */
.method-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  color: white;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
  min-width: 40px;
  text-align: center;
  flex-shrink: 0;
}

.method-tag.get {
  background-color: #61affe;
}

.method-tag.post {
  background-color: #49cc90;
}

.method-tag.put {
  background-color: #fca130;
}

.method-tag.delete {
  background-color: #f93e3e;
}

.method-tag.patch {
  background-color: #50e3c2;
}

.method-tag.head {
  background-color: #9013fe;
}

.method-tag.options {
  background-color: #0ebeff;
}

.method-tag.connect {
  background-color: #7f8c8d;
}

.method-tag.trace {
  background-color: #e67e22;
}

/* 搜索结果 */
.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 400px;
  overflow: auto;
  margin-top: 8px;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #f8f9fa;
  font-weight: 500;
  color: #303133;
}

.search-results-list {
  padding: 8px 0;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f0f2f5;
}

.search-result-item:hover {
  background: #ecf5ff;
}

.search-result-content {
  flex: 1;
  min-width: 0;
}

.search-result-name {
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.search-result-url {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 右侧主内容 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: auto;
  background: #f8f9fa;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}

.request-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  gap: 20px;
}

/* 请求头部 */
.request-header {
  margin-bottom: 0;
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s ease;
}

.request-header:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.request-line {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

/* 方法选择器样式 */
.method-select {
  width: 120px;
}

.method-select :deep(.el-select) {
  border-radius: 6px;
}

/* 为不同方法的选择器添加颜色 */
.method-select.get :deep(.el-select .el-input__wrapper) {
  background-color: #61affe !important;
  color: white !important;
  border-color: #61affe !important;
}

.method-select.post :deep(.el-select .el-input__wrapper) {
  background-color: #49cc90 !important;
  color: white !important;
  border-color: #49cc90 !important;
}

.method-select.put :deep(.el-select .el-input__wrapper) {
  background-color: #fca130 !important;
  color: white !important;
  border-color: #fca130 !important;
}

.method-select.delete :deep(.el-select .el-input__wrapper) {
  background-color: #f93e3e !important;
  color: white !important;
  border-color: #f93e3e !important;
}

.method-select.patch :deep(.el-select .el-input__wrapper) {
  background-color: #50e3c2 !important;
  color: white !important;
  border-color: #50e3c2 !important;
}

.method-select.head :deep(.el-select .el-input__wrapper) {
  background-color: #9013fe !important;
  color: white !important;
  border-color: #9013fe !important;
}

.method-select.options :deep(.el-select .el-input__wrapper) {
  background-color: #0ebeff !important;
  color: white !important;
  border-color: #0ebeff !important;
}

.method-select.connect :deep(.el-select .el-input__wrapper) {
  background-color: #7f8c8d !important;
  color: white !important;
  border-color: #7f8c8d !important;
}

.method-select.trace :deep(.el-select .el-input__wrapper) {
  background-color: #e67e22 !important;
  color: white !important;
  border-color: #e67e22 !important;
}

/* 方法选择器通用样式 */
.method-select :deep(.el-select .el-input__inner) {
  color: white !important;
}

.method-select :deep(.el-select .el-select__icon) {
  color: white !important;
}

.method-select :deep(.el-select .el-select__selected-item),
.method-select :deep(.el-select .el-select__selected-item span),
.method-select :deep(.el-select .el-select__placeholder) {
  background-color: transparent !important;
  color: white !important;
}

.method-select :deep(.el-select .el-input__wrapper .el-select__placeholder) {
  background-color: transparent !important;
  color: white !important;
}

.method-select :deep(.el-select .el-input__wrapper .el-input__inner::placeholder) {
  background-color: transparent !important;
  color: white !important;
}

.method-select :deep(.el-select .el-input__wrapper .el-input__inner::-webkit-input-placeholder) {
  background-color: transparent !important;
  color: white !important;
}

.method-select :deep(.el-select .el-input__wrapper .el-input__inner::-moz-placeholder) {
  background-color: transparent !important;
  color: white !important;
}

.method-select :deep(.el-select .el-input__wrapper .el-input__inner:-ms-input-placeholder) {
  background-color: transparent !important;
  color: white !important;
}

/* 方法选择器下拉菜单样式 */
.method-select :deep(.el-select-dropdown) {
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.method-select :deep(.el-select-dropdown__item) {
  padding: 8px 16px;
  border-radius: 4px;
}

.method-select :deep(.el-select-dropdown__item:hover) {
  background-color: #f0f0f0;
}

.method-select :deep(.el-select-dropdown__item.selected) {
  background-color: #ecf5ff;
  color: #409eff;
}

/* 为不同方法的下拉选项添加颜色 */
.method-select :deep(.el-select-dropdown__item[class*="method-"]) {
  position: relative;
}

.method-select :deep(.el-select-dropdown__item[class*="method-"])::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 0 4px 4px 0;
}

.method-select :deep(.el-select-dropdown__item.method-get::before) {
  background-color: #61affe;
}

.method-select :deep(.el-select-dropdown__item.method-post::before) {
  background-color: #49cc90;
}

.method-select :deep(.el-select-dropdown__item.method-put::before) {
  background-color: #fca130;
}

.method-select :deep(.el-select-dropdown__item.method-delete::before) {
  background-color: #f93e3e;
}

.method-select :deep(.el-select-dropdown__item.method-patch::before) {
  background-color: #50e3c2;
}

.method-select :deep(.el-select-dropdown__item.method-head::before) {
  background-color: #9013fe;
}

.method-select :deep(.el-select-dropdown__item.method-options::before) {
  background-color: #0ebeff;
}

.method-select :deep(.el-select-dropdown__item.method-connect::before) {
  background-color: #7f8c8d;
}

.method-select :deep(.el-select-dropdown__item.method-trace::before) {
  background-color: #e67e22;
}

.url-input {
  flex: 1;
  min-width: 200px;
}

.url-input .el-input {
  border-radius: 6px;
}

.env-select {
  width: 160px;
}

.env-select .el-select {
  border-radius: 6px;
}

.send-button {
  width: 100px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  background: #5046e5;
  border: none;
}

.send-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(80, 70, 229, 0.4);
  background: #4338ca;
}

/* 请求元数据 */
.request-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.name-input {
  flex: 1;
  min-width: 200px;
}

.name-input .el-input {
  border-radius: 6px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-buttons .el-button {
  border-radius: 6px;
  transition: all 0.2s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-buttons .el-dropdown {
  border-radius: 6px;
}

/* 标签页内容 */
.tab-content {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 24px;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 响应区域 */
.response-section {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s ease;
}

.response-section:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.response-header {
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.response-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.response-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.response-time {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  background: #e9ecef;
  padding: 4px 12px;
  border-radius: 16px;
}

/* 响应体 */
.response-body {
  padding: 24px;
  min-height: 400px;
  max-height: 600px;
  overflow: auto;
  background: #f8f9fa;
  border-radius: 10px;
  margin: 20px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.response-actions {
  margin-bottom: 16px;
}

.response-actions .el-button-group {
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.response-actions .el-button {
  border-radius: 0;
  transition: all 0.2s ease;
  background: transparent;
  border: none;
  color: #666;
}

.response-actions .el-button:hover {
  background: #f5f7fa;
  color: #5046e5;
}

.response-content {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  background: white;
  padding: 20px 20px 20px 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 响应头 */
.response-headers {
  padding: 24px;
  background: #f8f9fa;
  border-radius: 10px;
  margin: 20px;
  border: 1px solid #e9ecef;
  max-height: 80vh;
  overflow: auto;
}

.header-row {
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
}

.header-row:last-child {
  border-bottom: none;
}

/* 响应区域：一级 tab（响应信息 / 请求信息）切换，内部二级 tab 细分 */
.result-tabs {
  margin-top: 4px;
  padding: 0 20px 20px;
}

.result-tabs :deep(.el-tabs__header) {
  margin: 0 0 12px;
}

/* 嵌套的二级 tabs：去除默认大间距，紧贴上级 tab 内 */
.nested-tabs :deep(.el-tabs__header) {
  margin: 0 0 8px;
}

/* 请求行（方法 + URL） */
.request-line {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #ecf5ff;
  border-radius: 6px;
  border: 1px solid #d9ecff;
  margin-bottom: 8px;
}

.request-line strong {
  color: #409eff;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  flex-shrink: 0;
}

.request-url {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 13px;
  word-break: break-all;
  color: #303133;
  min-width: 0;
}

/* 空数据提示 */
.empty-tip {
  padding: 24px 16px;
  color: #909399;
  font-size: 13px;
  text-align: center;
  background: #f8f9fa;
  border-radius: 6px;
}

/* 代码编辑器 */
.code-editor {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 14px;
  line-height: 1.6;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  min-height: 200px;
  resize: vertical;
  transition: all 0.2s ease;
}

.code-editor:focus {
  outline: none;
  border-color: #5046e5;
  box-shadow: 0 0 0 2px rgba(80, 70, 229, 0.2);
}

.code-generate {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 14px;
  line-height: 1.6;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  min-height: 300px;
  resize: vertical;
}

/* 上下文菜单 */
.context-menu {
  position: fixed;
  z-index: 1000;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  min-width: 140px;
  list-style: none;
  margin: 0;
}

.context-menu li {
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #303133;
}

.context-menu li:hover {
  background: #f5f3ff;
  color: #5046e5;
  font-weight: 500;
}

/* 脚本编辑器容器 */
.script-editor-container {
  position: relative;
}

.script-editor-container .el-input {
  border-radius: 6px;
}

.script-editor-container .el-input__textarea {
  min-height: 200px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.6;
}

/* 脚本按钮 */
.script-buttons {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 6px;
  z-index: 10;
  background: white;
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.script-buttons .el-button {
  border-radius: 6px;
  font-size: 11px;
  padding: 4px 10px;
  transition: all 0.2s ease;
  background: transparent;
  border: none;
}

.script-buttons .el-button:hover {
  transform: none;
  box-shadow: none;
  background: #f5f7fa;
}

.script-factory-btn {
  color: #10b981;
}

.script-factory-btn:hover {
  background: #ecfdf5;
}

.script-variable-btn {
  color: #5046e5;
}

.script-variable-btn:hover {
  background: #f5f3ff;
}

/* Raw 选项 */
.raw-options {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  background: white;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.raw-options .el-select {
  width: 150px;
  border-radius: 6px;
}

.raw-options .el-button {
  border-radius: 6px;
  font-size: 11px;
  padding: 4px 10px;
  transition: all 0.2s ease;
  background: transparent;
  border: none;
}

.raw-options .el-button:hover {
  transform: none;
  box-shadow: none;
  background: #f5f7fa;
}

.data-factory-btn {
  background-color: #409eff !important;
  border-color: #409eff !important;
  color: white !important;
}

.data-factory-btn:hover {
  background-color: #66b1ff !important;
  border-color: #66b1ff !important;
}

.variable-helper-btn {
  background-color: #67c23a !important;
  border-color: #67c23a !important;
  color: white !important;
}

.variable-helper-btn:hover {
  background-color: #5daf34 !important;
  border-color: #5daf34 !important;
}

.raw-body {
  border-radius: 6px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.6;
}

/* 断言编辑器 */
.assertions-editor {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.assertions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
}

.assertions-header .el-button {
  border-radius: 8px;
  background: #5046e5;
  border: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.assertions-header .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(80, 70, 229, 0.4);
  background: #4338ca;
}

.assertions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 变量提取编辑器 */
.extract-editor {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.extract-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
}

.extract-header .el-button {
  border-radius: 8px;
  font-weight: 500;
}

.extract-hint {
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
}

.extract-table {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.extract-row {
  display: grid;
  grid-template-columns: 1.2fr 0.9fr 1.6fr 0.9fr 0.9fr 56px;
  gap: 10px;
  align-items: center;
}

.extract-row-head {
  color: #606266;
  font-size: 12px;
  font-weight: 600;
  padding: 0 2px;
}

.extract-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

/* 断言项 */
.assertion-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.assertion-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #dee2e6;
}

.assertion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.assertion-name {
  flex: 1;
  margin-right: 12px;
  border-radius: 6px;
}

.assertion-config {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assertion-config .el-select {
  width: 200px;
  border-radius: 6px;
}

.assertion-params {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assertion-input {
  margin-bottom: 12px;
  border-radius: 6px;
}

/* 标签页按钮 */
.tab-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-button {
  padding: 10px 20px;
  border: 1px solid #e4e7ed;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #606266;
}

.tab-button.active {
  background: #409eff;
  color: white;
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.tab-button:hover:not(.active) {
  border-color: #c6e2ff;
  color: #409eff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 表单行 */
.form-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.form-label {
  width: 100px;
  font-weight: 500;
  color: #303133;
  flex-shrink: 0;
}

.form-input {
  flex: 1;
  min-width: 200px;
}

.form-input .el-input {
  border-radius: 6px;
}

/* 字符串构建器 */
.string-builder {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.string-builder-header {
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.string-builder-body {
  padding: 16px;
  min-height: 120px;
  background: white;
}

.string-builder-footer {
  padding: 12px 16px;
  background: #f8f9fa;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.string-builder-footer .el-button {
  border-radius: 6px;
}

/* 变量助手 */
.variable-assistant {
  position: relative;
}

.variable-popup {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  width: 450px;
  max-height: 500px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  margin-top: 8px;
}

.variable-header {
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.variable-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.variable-content {
  flex: 1;
  overflow: auto;
}

.variable-categories {
  padding: 16px;
}

.variable-category {
  margin-bottom: 24px;
}

.variable-category-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
  font-size: 14px;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 6px;
}

.variable-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.variable-item {
  padding: 14px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.variable-item:hover {
  background: #ecf5ff;
  border-color: #c6e2ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.variable-name {
  font-weight: 500;
  margin-bottom: 6px;
  color: #303133;
}

.variable-syntax {
  font-size: 12px;
  color: #909399;
  font-family: 'Courier New', Courier, monospace;
  margin-bottom: 6px;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.variable-desc {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.variable-example {
  font-size: 12px;
  color: #67c23a;
  font-family: 'Courier New', Courier, monospace;
  margin-top: 4px;
  background: #f0f9eb;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #c2e7b0;
}

/* JSONPath 部分 */
.jsonpath-extractor {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.jsonpath-input {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
}

.jsonpath-input .el-input {
  flex: 1;
  border-radius: 6px;
}

.jsonpath-result {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  min-height: 80px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow: auto;
}

/* 状态徽章 */
.status-badge {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 500;
}

.status-badge.success {
  background: #f0f9eb;
  color: #67c23a;
}

.status-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.status-badge.danger {
  background: #fef0f0;
  color: #f56c6c;
}

.status-badge.info {
  background: #ecf5ff;
  color: #409eff;
}

/* 断言结果 */
.assertions-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.assertion-result-item {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.assertion-result-item.passed {
  border-left: 4px solid #67c23a;
}

.assertion-result-item.failed {
  border-left: 4px solid #f56c6c;
}

.assertion-result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.assertion-result-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 20px;
}

.result-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.result-row .label {
  width: 80px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  flex-shrink: 0;
}

.result-row .value {
  flex: 1;
  font-size: 14px;
  color: #303133;
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.result-row .value.error {
  color: #f56c6c;
}

/* WebSocket 相关 */
.message-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-input-section {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
}

.message-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 16px;
}

.message-actions .el-button {
  border-radius: 6px;
  transition: all 0.2s ease;
}

.message-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.websocket-response-section {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
}

.websocket-response-section h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.websocket-messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow: auto;
  padding: 10px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.websocket-message-item {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  background: white;
}

.websocket-message-item.sent {
  border-left: 4px solid #409eff;
  background: #ecf5ff;
}

.websocket-message-item.received {
  border-left: 4px solid #67c23a;
  background: #f0f9eb;
}

.websocket-message-item.connected {
  border-left: 4px solid #67c23a;
  background: #f0f9eb;
}

.websocket-message-item.info {
  border-left: 4px solid #909399;
  background: #f5f7fa;
}

.websocket-message-item.error {
  border-left: 4px solid #f56c6c;
  background: #fef0f0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
}

.message-type {
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
}

.message-type.sent {
  background: #d9ecff;
  color: #409eff;
}

.message-type.received {
  background: #e8f5e8;
  color: #67c23a;
}

.message-type.connected {
  background: #e8f5e8;
  color: #67c23a;
}

.message-type.info {
  background: #f0f2f5;
  color: #909399;
}

.message-type.error {
  background: #fde2e2;
  color: #f56c6c;
}

.message-time {
  color: #909399;
}

.message-content {
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}

.uploaded-file {
  margin-top: 12px;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .interface-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    max-height: 300px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }

  .request-line {
    flex-direction: column;
    align-items: stretch;
  }

  .method-select,
  .url-input,
  .env-select,
  .send-button {
    width: 100%;
  }

  .form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .form-label {
    width: 100%;
    margin-bottom: 8px;
  }

  .script-buttons {
    position: static;
    margin-top: 12px;
    justify-content: flex-end;
  }

  .request-meta {
    flex-direction: column;
    align-items: stretch;
  }

  .name-input {
    width: 100%;
  }

  .action-buttons {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .tab-buttons {
    justify-content: flex-start;
  }

  .tab-button {
    padding: 8px 16px;
    font-size: 13px;
  }

  .raw-options {
    flex-direction: column;
    align-items: stretch;
  }

  .raw-options .el-select {
    width: 100%;
  }

  .raw-options .el-button {
    width: 100%;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 覆盖方法标签样式 */
.method-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  color: white;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
  min-width: 40px;
  text-align: center;
  flex-shrink: 0;
}

.method-tag.get {
  background-color: #61affe !important;
}

.method-tag.post {
  background-color: #49cc90 !important;
}

.method-tag.put {
  background-color: #fca130 !important;
}

.method-tag.delete {
  background-color: #f93e3e !important;
}

.method-tag.patch {
  background-color: #50e3c2 !important;
}

.method-tag.head {
  background-color: #9013fe !important;
}

.method-tag.options {
  background-color: #0ebeff !important;
}

.method-tag.connect {
  background-color: #7f8c8d !important;
}

.method-tag.trace {
  background-color: #e67e22 !important;
}

/* 覆盖方法选择器样式 */
.method-select.get :deep(.el-select .el-input__wrapper) {
  background-color: #61affe !important;
  color: white !important;
  border-color: #61affe !important;
}

.method-select.post :deep(.el-select .el-input__wrapper) {
  background-color: #49cc90 !important;
  color: white !important;
  border-color: #49cc90 !important;
}

.method-select.put :deep(.el-select .el-input__wrapper) {
  background-color: #fca130 !important;
  color: white !important;
  border-color: #fca130 !important;
}

.method-select.delete :deep(.el-select .el-input__wrapper) {
  background-color: #f93e3e !important;
  color: white !important;
  border-color: #f93e3e !important;
}

.method-select.patch :deep(.el-select .el-input__wrapper) {
  background-color: #50e3c2 !important;
  color: white !important;
  border-color: #50e3c2 !important;
}

.method-select.head :deep(.el-select .el-input__wrapper) {
  background-color: #9013fe !important;
  color: white !important;
  border-color: #9013fe !important;
}

.method-select.options :deep(.el-select .el-input__wrapper) {
  background-color: #0ebeff !important;
  color: white !important;
  border-color: #0ebeff !important;
}

.method-select.connect :deep(.el-select .el-input__wrapper) {
  background-color: #7f8c8d !important;
  color: white !important;
  border-color: #7f8c8d !important;
}

.method-select.trace :deep(.el-select .el-input__wrapper) {
  background-color: #e67e22 !important;
  color: white !important;
  border-color: #e67e22 !important;
}

/* 覆盖方法选择器通用样式 */
.method-select :deep(.el-select .el-input__inner) {
  color: white !important;
}

.method-select :deep(.el-select .el-select__icon) {
  color: white !important;
}

.method-select :deep(.el-select .el-select__selected-item),
.method-select :deep(.el-select .el-select__selected-item span),
.method-select :deep(.el-select .el-select__placeholder) {
  background-color: transparent !important;
  color: white !important;
}

</style>
