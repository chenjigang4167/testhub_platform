<template>
  <div class="data-factory-container">
    <el-card class="header-card">
      <div class="header-content">
        <h1 class="page-title" @click="goToHome">
          <el-icon class="title-icon"><DataLine /></el-icon>
          {{ $t('dataFactory.title') }}
        </h1>
        <p class="page-subtitle">{{ $t('dataFactory.subtitle') }}</p>
        <div class="header-actions">
          <el-button-group>
            <el-button
              :type="viewMode === 'category' ? 'primary' : ''"
              @click="viewMode = 'category'"
            >
              <el-icon><Menu /></el-icon>
              {{ $t('dataFactory.viewMode.category') }}
            </el-button>
            <el-button
              :type="viewMode === 'scenario' ? 'primary' : ''"
              @click="viewMode = 'scenario'"
            >
              <el-icon><Grid /></el-icon>
              {{ $t('dataFactory.viewMode.scenario') }}
            </el-button>
          </el-button-group>
          <el-button type="info" @click="showHistory = true">
            <el-icon><Clock /></el-icon>
            {{ $t('dataFactory.actions.history') }}
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 工具分类视图 -->
    <div v-if="viewMode === 'category'" class="category-view">
      <div
        v-for="category in filteredCategories()"
        :key="category.category"
        class="category-section"
      >
        <el-card class="category-card">
          <template #header>
            <div class="category-header">
              <el-icon :class="`category-icon ${category.icon}`">
                <component :is="getIcon(category.icon)" />
              </el-icon>
              <span class="category-title">{{ getCategoryName(category.category) }}</span>
              <el-tag size="small">{{ $t('dataFactory.toolCount', { count: category.tools.length }) }}</el-tag>
              <el-button
                v-if="currentScenario"
                size="small"
                @click.stop="clearScenario"
                style="margin-left: auto;"
              >
                {{ $t('dataFactory.actions.clearFilter') }}
              </el-button>
            </div>
          </template>
          <div class="tools-grid">
            <div
              v-for="tool in category.tools"
              :key="tool.name"
              class="tool-item"
              @click="openTool(tool, category.category)"
            >
              <div class="tool-icon">
                <el-icon><component :is="getIcon(tool.icon || 'operation')" /></el-icon>
              </div>
              <div class="tool-info">
                <h4 class="tool-name">{{ getToolDisplayName(tool.name) || tool.display_name }}</h4>
                <p class="tool-desc">{{ getToolDescription(tool.name) || tool.description }}</p>
              </div>
              <el-icon class="tool-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 场景视图 -->
    <div v-else class="scenario-view">
      <el-row :gutter="20">
        <el-col :span="8" v-for="scenario in scenarios" :key="scenario.scenario">
          <el-card class="scenario-card" @click="filterByScenario(scenario)">
            <div class="scenario-content">
              <el-icon class="scenario-icon">
                <component :is="getScenarioIcon(scenario.scenario)" />
              </el-icon>
              <h3 class="scenario-title">{{ getScenarioName(scenario.scenario) }}</h3>
              <p class="scenario-desc">{{ getScenarioDesc(scenario.scenario) }}</p>
              <div class="scenario-stats">
                <el-tag size="small">{{ $t('dataFactory.toolCount', { count: scenario.tool_count }) }}</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 工具执行对话框 -->
    <el-dialog
      v-model="toolDialogVisible"
      :title="getToolDisplayName(currentTool?.name) || currentTool?.display_name"
      width="1200px"
      :close-on-click-modal="false"
      @close="resetToolForm"
    >
      <div v-if="currentTool" class="tool-execution">
        <el-alert
          :title="getToolDescription(currentTool?.name) || currentTool.description"
          type="info"
          :closable="false"
          show-icon
          class="tool-alert"
        />

        <!-- 测试数据工具 - 无需输入参数 -->
        <div v-if="currentCategory === 'test_data'" class="tool-form">
          <el-form label-width="120px">
            <el-form-item :label="$t('dataFactory.form.count')">
              <el-input-number v-model="toolForm.count" :min="1" :max="100" />
              <span class="form-tip">{{ $t('dataFactory.form.countTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_chinese_phone'" :label="$t('dataFactory.form.carrier')">
              <el-select v-model="toolForm.region" :placeholder="$t('dataFactory.form.carrier')">
                <el-option :label="$t('dataFactory.form.carrierOptions.all')" value="all" />
                <el-option :label="$t('dataFactory.form.carrierOptions.mobile')" value="mobile" />
                <el-option :label="$t('dataFactory.form.carrierOptions.unicom')" value="unicom" />
                <el-option :label="$t('dataFactory.form.carrierOptions.telecom')" value="telecom" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_chinese_email'" :label="$t('dataFactory.form.emailDomain')">
              <el-select v-model="toolForm.domain" :placeholder="$t('dataFactory.form.emailDomain')">
                <el-option :label="$t('dataFactory.form.emailDomainOptions.random')" value="random" />
                <el-option :label="$t('dataFactory.form.emailDomainOptions.qq')" value="qq.com" />
                <el-option :label="$t('dataFactory.form.emailDomainOptions.netease163')" value="163.com" />
                <el-option :label="$t('dataFactory.form.emailDomainOptions.netease126')" value="126.com" />
                <el-option :label="$t('dataFactory.form.emailDomainOptions.gmail')" value="gmail.com" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_chinese_address'" :label="$t('dataFactory.form.addressType')">
              <el-switch v-model="toolForm.full_address" :active-text="$t('dataFactory.form.fullAddress')" :inactive-text="$t('dataFactory.form.shortAddress')" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 字符工具 -->
        <div v-else-if="currentCategory === 'string'" class="tool-form">
          <el-form label-width="120px">
            <el-form-item v-if="currentTool.name !== 'text_diff'" :label="$t('dataFactory.form.inputText')">
              <el-input
                v-model="toolForm.text"
                type="textarea"
                :rows="4"
                :placeholder="$t('dataFactory.form.inputText') + '...'"
              />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'replace_string'" :label="$t('dataFactory.form.findContent')">
              <el-input v-model="toolForm.old_str" :placeholder="$t('dataFactory.form.findContentPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'replace_string'" :label="$t('dataFactory.form.replaceContent')">
              <el-input v-model="toolForm.new_str" :placeholder="$t('dataFactory.form.replaceContentPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'replace_string'" :label="$t('dataFactory.form.regex')">
              <el-switch v-model="toolForm.is_regex" />
              <span class="form-tip">{{ $t('dataFactory.form.regexTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'escape_string'" :label="$t('dataFactory.form.escapeType')">
              <el-select v-model="toolForm.escape_type" :placeholder="$t('dataFactory.form.escapeType')">
                <el-option label="JSON" value="json" />
                <el-option label="HTML" value="html" />
                <el-option label="URL" value="url" />
                <el-option label="XML" value="xml" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'unescape_string'" :label="$t('dataFactory.form.unescapeType')">
              <el-select v-model="toolForm.unescape_type" :placeholder="$t('dataFactory.form.unescapeType')">
                <el-option label="JSON" value="json" />
                <el-option label="HTML" value="html" />
                <el-option label="URL" value="url" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'regex_test'" :label="$t('dataFactory.form.regex')">
              <el-input v-model="toolForm.pattern" :placeholder="$t('dataFactory.form.regexPatternPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'regex_test'" :label="$t('dataFactory.form.flags')">
              <el-checkbox-group v-model="toolForm.flags">
                <el-checkbox label="i">{{ $t('dataFactory.form.flagIgnoreCase') }}</el-checkbox>
                <el-checkbox label="m">{{ $t('dataFactory.form.flagMultiline') }}</el-checkbox>
                <el-checkbox label="s">{{ $t('dataFactory.form.flagSingleline') }}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'case_convert'" :label="$t('dataFactory.form.convertType')">
              <el-select v-model="toolForm.convert_type" :placeholder="$t('dataFactory.form.convertType')">
                <el-option :label="$t('dataFactory.form.convertTypeOptions.upper')" value="upper" />
                <el-option :label="$t('dataFactory.form.convertTypeOptions.lower')" value="lower" />
                <el-option :label="$t('dataFactory.form.convertTypeOptions.capitalize')" value="capitalize" />
                <el-option :label="$t('dataFactory.form.convertTypeOptions.title')" value="title" />
                <el-option :label="$t('dataFactory.form.convertTypeOptions.swapcase')" value="swapcase" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'string_format'" :label="$t('dataFactory.form.formatType')">
              <el-select v-model="toolForm.format_type" :placeholder="$t('dataFactory.form.formatType')">
                <el-option :label="$t('dataFactory.form.formatTypeOptions.trim')" value="trim" />
                <el-option :label="$t('dataFactory.form.formatTypeOptions.reverse')" value="reverse" />
                <el-option :label="$t('dataFactory.form.formatTypeOptions.split')" value="split" />
                <el-option :label="$t('dataFactory.form.formatTypeOptions.join')" value="join" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'text_diff'" :label="$t('dataFactory.form.text1')">
              <el-input
                v-model="toolForm.text1"
                type="textarea"
                :rows="6"
                :placeholder="$t('dataFactory.form.text1Placeholder')"
              />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'text_diff'" :label="$t('dataFactory.form.text2')">
              <el-input
                v-model="toolForm.text2"
                type="textarea"
                :rows="6"
                :placeholder="$t('dataFactory.form.text2Placeholder')"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 随机工具 -->
        <div v-else-if="currentCategory === 'random'" class="tool-form">
          <el-form label-width="120px">
            <el-form-item v-if="currentTool.name === 'random_int'" :label="$t('dataFactory.form.minValue')">
              <el-input-number v-model="toolForm.min_val" :min="-999999" :max="999999" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_int'" :label="$t('dataFactory.form.maxValue')">
              <el-input-number v-model="toolForm.max_val" :min="-999999" :max="999999" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_float'" :label="$t('dataFactory.form.minValue')">
              <el-input-number v-model="toolForm.min_val" :step="0.1" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_float'" :label="$t('dataFactory.form.maxValue')">
              <el-input-number v-model="toolForm.max_val" :step="0.1" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_float'" :label="$t('dataFactory.form.precision')">
              <el-input-number v-model="toolForm.precision" :min="0" :max="10" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_string'" :label="$t('dataFactory.form.length')">
              <el-input-number v-model="toolForm.length" :min="1" :max="1000" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_string'" :label="$t('dataFactory.form.charType')">
              <el-select v-model="toolForm.char_type" :placeholder="$t('dataFactory.form.charType')">
                <el-option :label="$t('dataFactory.form.charTypeOptions.all')" value="all" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.letters')" value="letters" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.lowercase')" value="lowercase" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.uppercase')" value="uppercase" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.digits')" value="digits" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.alphanumeric')" value="alphanumeric" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.hex')" value="hex" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.chinese')" value="chinese" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.special')" value="special" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_uuid'" :label="$t('dataFactory.form.uuidVersion')">
              <el-select v-model="toolForm.version" :placeholder="$t('dataFactory.form.uuidVersion')">
                <el-option label="UUID v1" :value="1" />
                <el-option label="UUID v4" :value="4" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_mac_address'" :label="$t('dataFactory.form.separator')">
              <el-select v-model="toolForm.separator" :placeholder="$t('dataFactory.form.separator')">
                <el-option :label="$t('dataFactory.form.separatorOptions.colon')" value=":" />
                <el-option :label="$t('dataFactory.form.separatorOptions.hyphen')" value="-" />
                <el-option :label="$t('dataFactory.form.separatorOptions.none')" value="" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_ip_address'" :label="$t('dataFactory.form.ipVersion')">
              <el-select v-model="toolForm.ip_version" :placeholder="$t('dataFactory.form.ipVersion')">
                <el-option label="IPv4" :value="4" />
                <el-option label="IPv6" :value="6" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_date'" :label="$t('dataFactory.form.startDate')">
              <el-date-picker v-model="toolForm.start_date" type="date" :placeholder="$t('dataFactory.form.selectStartDate')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_date'" :label="$t('dataFactory.form.endDate')">
              <el-date-picker v-model="toolForm.end_date" type="date" :placeholder="$t('dataFactory.form.selectEndDate')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_date'" :label="$t('dataFactory.form.dateFormat')">
              <el-input v-model="toolForm.date_format" placeholder="%Y-%m-%d" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_color'" :label="$t('dataFactory.form.colorFormat')">
              <el-select v-model="toolForm.format" :placeholder="$t('dataFactory.form.colorFormat')">
                <el-option :label="$t('dataFactory.form.colorFormatOptions.hex')" value="hex" />
                <el-option :label="$t('dataFactory.form.colorFormatOptions.rgb')" value="rgb" />
                <el-option :label="$t('dataFactory.form.colorFormatOptions.rgba')" value="rgba" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_password'" :label="$t('dataFactory.form.passwordLength')">
              <el-input-number v-model="toolForm.length" :min="4" :max="50" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_password'" :label="$t('dataFactory.form.charOptions')">
              <el-checkbox-group v-model="toolForm.char_options">
                <el-checkbox label="include_uppercase">{{ $t('dataFactory.form.charOptionsItems.uppercase') }}</el-checkbox>
                <el-checkbox label="include_lowercase">{{ $t('dataFactory.form.charOptionsItems.lowercase') }}</el-checkbox>
                <el-checkbox label="include_digits">{{ $t('dataFactory.form.charOptionsItems.digits') }}</el-checkbox>
                <el-checkbox label="include_special">{{ $t('dataFactory.form.charOptionsItems.special') }}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item v-if="['random_int', 'random_float', 'random_string', 'random_uuid', 'random_mac_address', 'random_ip_address', 'random_date', 'random_boolean', 'random_color', 'random_password', 'random_sequence'].includes(currentTool.name)" :label="$t('dataFactory.form.count')">
              <el-input-number v-model="toolForm.count" :min="1" :max="100" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_sequence'" :label="$t('dataFactory.form.sequenceData')">
              <el-input v-model="toolForm.sequence" type="textarea" :rows="4" :placeholder="$t('dataFactory.form.sequenceDataPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'random_sequence'" :label="$t('dataFactory.form.unique')">
              <el-switch v-model="toolForm.unique" />
              <span class="form-tip">{{ $t('dataFactory.form.uniqueTip') }}</span>
            </el-form-item>
          </el-form>
        </div>

        <!-- 编码工具 -->
        <div v-else-if="currentCategory === 'encoding'" class="tool-form">
          <el-form label-width="120px">
            <el-form-item v-if="['generate_barcode', 'generate_qrcode'].includes(currentTool.name)" :label="$t('dataFactory.form.data')">
              <el-input v-model="toolForm.data" :placeholder="$t('dataFactory.form.data')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_barcode'" :label="$t('dataFactory.form.barcodeType')">
              <el-select v-model="toolForm.barcode_type" :placeholder="$t('dataFactory.form.barcodeType')">
                <el-option label="Code128" value="code128" />
                <el-option label="Code39" value="code39" />
                <el-option label="EAN13" value="ean13" />
                <el-option label="EAN8" value="ean8" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_qrcode'" :label="$t('dataFactory.form.imageSize')">
              <el-input-number v-model="toolForm.image_size" :min="100" :max="1000" :step="50" />
              <span class="form-tip">{{ $t('dataFactory.form.imageSizeTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'decode_qrcode'" :label="$t('dataFactory.form.uploadQrCode')">
              <el-upload
                class="qr-code-upload"
                :show-file-list="false"
                :before-upload="handleQrCodeUpload"
                accept="image/*"
                drag
              >
                <div v-if="!qrCodeImage" class="upload-placeholder">
                  <el-icon class="upload-icon"><Upload /></el-icon>
                  <div class="upload-text">{{ $t('dataFactory.form.uploadQrCodeText') }}</div>
                  <div class="upload-tip">{{ $t('dataFactory.form.uploadQrCodeTip') }}</div>
                </div>
                <div v-else class="upload-preview">
                  <img :src="qrCodeImage" :alt="$t('dataFactory.form.qrCodePreview')" />
                  <div class="upload-mask" @click="clearQrCodeImage">
                    <el-icon><Delete /></el-icon>
                    <span>{{ $t('dataFactory.form.clickToDelete') }}</span>
                  </div>
                </div>
              </el-upload>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'timestamp_convert'" :label="$t('dataFactory.form.timestampOrDate')">
              <el-input v-model="toolForm.timestamp" :placeholder="$t('dataFactory.form.timestampPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'timestamp_convert'" :label="$t('dataFactory.form.timestampConvertType')">
              <el-select v-model="toolForm.timestamp_convert_type" :placeholder="$t('dataFactory.form.timestampConvertType')">
                <el-option :label="$t('dataFactory.form.timestampConvertOptions.toDatetime')" value="to_datetime" />
                <el-option :label="$t('dataFactory.form.timestampConvertOptions.toTimestamp')" value="to_timestamp" />
                <el-option :label="$t('dataFactory.form.timestampConvertOptions.currentTimestamp')" value="current_timestamp" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'timestamp_convert' && toolForm.timestamp_convert_type === 'to_datetime'" :label="$t('dataFactory.form.timestampUnit')">
              <el-select v-model="toolForm.timestamp_unit" :placeholder="$t('dataFactory.form.timestampUnit')">
                <el-option :label="$t('dataFactory.form.timestampUnitOptions.auto')" value="auto" />
                <el-option :label="$t('dataFactory.form.timestampUnitOptions.second')" value="second" />
                <el-option :label="$t('dataFactory.form.timestampUnitOptions.millisecond')" value="millisecond" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'base_convert'" :label="$t('dataFactory.form.numberValue')">
              <el-input v-model="toolForm.number" :placeholder="$t('dataFactory.form.numberValuePlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'base_convert'" :label="$t('dataFactory.form.fromBase')">
              <el-input-number v-model="toolForm.from_base" :min="2" :max="36" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'base_convert'" :label="$t('dataFactory.form.toBase')">
              <el-input-number v-model="toolForm.to_base" :min="2" :max="36" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'unicode_convert'" :label="$t('dataFactory.form.text')">
              <el-input v-model="toolForm.text" :placeholder="$t('dataFactory.form.inputText')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'unicode_convert'" :label="$t('dataFactory.form.unicodeConvertType')">
              <el-select v-model="toolForm.unicode_convert_type" :placeholder="$t('dataFactory.form.unicodeConvertType')">
                <el-option :label="$t('dataFactory.form.unicodeConvertOptions.toUnicode')" value="to_unicode" />
                <el-option :label="$t('dataFactory.form.unicodeConvertOptions.fromUnicode')" value="from_unicode" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'ascii_convert'" :label="$t('dataFactory.form.text')">
              <el-input v-model="toolForm.text" :placeholder="$t('dataFactory.form.inputText')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'ascii_convert'" :label="$t('dataFactory.form.asciiConvertType')">
              <el-select v-model="toolForm.convert_type" :placeholder="$t('dataFactory.form.asciiConvertType')">
                <el-option :label="$t('dataFactory.form.asciiConvertOptions.toAscii')" value="to_ascii" />
                <el-option :label="$t('dataFactory.form.asciiConvertOptions.fromAscii')" value="from_ascii" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'color_convert'" :label="$t('dataFactory.form.colorValue')">
              <el-input v-model="toolForm.color" :placeholder="$t('dataFactory.form.colorValuePlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'color_convert'" :label="$t('dataFactory.form.sourceFormat')">
              <el-select v-model="toolForm.from_type" :placeholder="$t('dataFactory.form.sourceFormat')">
                <el-option :label="$t('dataFactory.form.colorFormatOptions.hex')" value="hex" />
                <el-option :label="$t('dataFactory.form.colorFormatOptions.rgb')" value="rgb" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'color_convert'" :label="$t('dataFactory.form.targetFormat')">
              <el-select v-model="toolForm.to_type" :placeholder="$t('dataFactory.form.targetFormat')">
                <el-option :label="$t('dataFactory.form.colorFormatOptions.hex')" value="hex" />
                <el-option :label="$t('dataFactory.form.colorFormatOptions.rgb')" value="rgb" />
                <el-option :label="$t('dataFactory.form.colorFormatOptions.rgba')" value="rgba" />
                <el-option label="HSL" value="hsl" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="['base64_encode', 'base64_decode'].includes(currentTool.name)" :label="$t('dataFactory.form.text')">
              <el-input v-model="toolForm.text" type="textarea" :rows="4" :placeholder="$t('dataFactory.form.inputText')" />
            </el-form-item>
            <el-form-item v-if="['base64_encode', 'base64_decode'].includes(currentTool.name)" :label="$t('dataFactory.form.encoding')">
              <el-input v-model="toolForm.encoding" placeholder="utf-8" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'url_encode'" :label="$t('dataFactory.form.urlData')">
              <el-input v-model="toolForm.data" type="textarea" :rows="4" :placeholder="$t('dataFactory.form.urlDataEncodePlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'url_encode'" :label="$t('dataFactory.form.encodeMethod')">
              <el-select v-model="toolForm.plus" :placeholder="$t('dataFactory.form.encodeMethod')">
                <el-option :label="$t('dataFactory.form.encodeMethodOptions.standard')" :value="false" />
                <el-option :label="$t('dataFactory.form.encodeMethodOptions.plus')" :value="true" />
              </el-select>
              <span class="form-tip">{{ $t('dataFactory.form.plusEncodeTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'url_decode'" :label="$t('dataFactory.form.urlData')">
              <el-input v-model="toolForm.data" type="textarea" :rows="4" :placeholder="$t('dataFactory.form.urlDataDecodePlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'url_decode'" :label="$t('dataFactory.form.decodeMethod')">
              <el-select v-model="toolForm.plus" :placeholder="$t('dataFactory.form.decodeMethod')">
                <el-option :label="$t('dataFactory.form.decodeMethodOptions.standard')" :value="false" />
                <el-option :label="$t('dataFactory.form.decodeMethodOptions.plus')" :value="true" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'jwt_decode'" :label="$t('dataFactory.form.jwtToken')">
              <el-input v-model="toolForm.token" type="textarea" :rows="6" :placeholder="$t('dataFactory.form.jwtTokenPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'jwt_decode'" :label="$t('dataFactory.form.verifySignature')">
              <el-switch v-model="toolForm.verify" />
              <span class="form-tip">{{ $t('dataFactory.form.verifySignatureTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'jwt_decode' && toolForm.verify" :label="$t('dataFactory.form.secretKey')">
              <el-input v-model="toolForm.secret" type="password" :placeholder="$t('dataFactory.form.secretKeyPlaceholder')" show-password />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'image_to_base64'" :label="$t('dataFactory.form.uploadImage')">
              <el-upload
                ref="uploadRef"
                class="image-upload"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleImageChange"
                accept="image/*"
              >
                <el-button type="primary">{{ $t('dataFactory.actions.selectImage') }}</el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    {{ $t('dataFactory.form.uploadImageTip') }}
                  </div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'image_to_base64' && imagePreview" :label="$t('dataFactory.form.imagePreview')">
              <div class="image-preview">
                <img :src="imagePreview" :alt="$t('dataFactory.image.preview')" />
              </div>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'image_to_base64'" :label="$t('dataFactory.form.imageFormat')">
              <el-select v-model="toolForm.image_format" :placeholder="$t('dataFactory.form.selectImageFormat')">
                <el-option label="PNG" value="png" />
                <el-option label="JPEG" value="jpeg" />
                <el-option label="GIF" value="gif" />
                <el-option label="WebP" value="webp" />
                <el-option label="BMP" value="bmp" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'image_to_base64'" :label="$t('dataFactory.form.includePrefix')">
              <el-switch v-model="toolForm.include_prefix" />
              <span class="form-tip">{{ $t('dataFactory.form.includePrefixTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'base64_to_image'" :label="$t('dataFactory.form.base64Code')">
              <el-input v-model="toolForm.base64_str" type="textarea" :rows="10" :placeholder="$t('dataFactory.form.base64CodePlaceholder')" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 加密工具 -->
        <div v-else-if="currentCategory === 'encryption'" class="tool-form">
          <el-form label-width="120px">
            <el-form-item v-if="['md5_hash', 'sha1_hash', 'sha256_hash', 'sha512_hash', 'password_strength'].includes(currentTool.name)" :label="$t('dataFactory.form.text')">
              <el-input v-model="toolForm.text" type="textarea" :rows="4" :placeholder="$t('dataFactory.form.inputText')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'hash_comparison'" :label="$t('dataFactory.form.text')">
              <el-input v-model="toolForm.text" :placeholder="$t('dataFactory.form.inputText')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'hash_comparison'" :label="$t('dataFactory.form.hashValue')">
              <el-input v-model="toolForm.hash_value" :placeholder="$t('dataFactory.form.hashValuePlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'hash_comparison'" :label="$t('dataFactory.form.algorithm')">
              <el-select v-model="toolForm.algorithm" :placeholder="$t('dataFactory.form.algorithm')">
                <el-option label="MD5" value="md5" />
                <el-option label="SHA1" value="sha1" />
                <el-option label="SHA256" value="sha256" />
                <el-option label="SHA512" value="sha512" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="['aes_encrypt', 'aes_decrypt'].includes(currentTool.name)" :label="$t('dataFactory.form.text')">
              <el-input v-model="toolForm.text" type="textarea" :rows="4" :placeholder="$t('dataFactory.form.inputText')" />
            </el-form-item>
            <el-form-item v-if="['aes_encrypt', 'aes_decrypt'].includes(currentTool.name)" :label="$t('dataFactory.form.password')">
              <el-input v-model="toolForm.password" type="password" :placeholder="$t('dataFactory.form.passwordPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="['aes_encrypt', 'aes_decrypt'].includes(currentTool.name)" :label="$t('dataFactory.form.mode')">
              <el-select v-model="toolForm.mode" :placeholder="$t('dataFactory.form.mode')">
                <el-option label="CBC" value="CBC" />
                <el-option label="ECB" value="ECB" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_salt'" :label="$t('dataFactory.form.length')">
              <el-input-number v-model="toolForm.length" :min="8" :max="64" />
            </el-form-item>
            <el-form-item v-if="['base64_encode', 'base64_decode'].includes(currentTool.name)" :label="$t('dataFactory.form.text')">
              <el-input v-model="toolForm.text" type="textarea" :rows="4" :placeholder="$t('dataFactory.form.inputText')" />
            </el-form-item>
            <el-form-item v-if="['base64_encode', 'base64_decode'].includes(currentTool.name)" :label="$t('dataFactory.form.encoding')">
              <el-input v-model="toolForm.encoding" placeholder="utf-8" />
            </el-form-item>
          </el-form>
        </div>

        <!-- JSONPath查询工具 - 上下布局 -->
        <div v-else-if="currentCategory === 'json' && ['jsonpath_query'].includes(currentTool.name)" class="tool-form json-path-tool">
          <el-row :gutter="20">
            <el-col :span="24">
              <div class="path-input-panel">
                <h4>{{ $t('dataFactory.form.jsonPathExpr') }}</h4>
                <el-input
                  v-model="toolForm.jsonpath_expr"
                  :placeholder="$t('dataFactory.form.jsonPathExprPlaceholder')"
                  @input="handleJsonPathInput"
                />
                <div class="form-tip">
                  <a href="https://goessner.net/articles/JsonPath/" target="_blank">{{ $t('dataFactory.form.jsonPathSyntaxRef') }}</a>
                </div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="json-input-panel">
                <h4>{{ $t('dataFactory.form.jsonDataInput') }}</h4>
                <el-input
                  v-model="toolForm.json_str"
                  type="textarea"
                  :rows="15"
                  :placeholder="$t('dataFactory.form.jsonDataPlaceholder')"
                  @input="handleJsonPathInput"
                />
              </div>
            </el-col>
            <el-col :span="12">
              <div class="json-input-panel">
                <h4>{{ $t('dataFactory.form.queryResult') }}</h4>
                <div v-if="toolResult" class="result-display">
                  <pre>{{ JSON.stringify(toolResult.result || toolResult, null, 2) }}</pre>
                </div>
                <div v-else class="result-empty">
                  <el-empty :description="$t('dataFactory.form.queryResultEmpty')" :image-size="60" />
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- JSON对比工具 - 左右分栏布局 -->
        <div v-else-if="currentCategory === 'json' && ['json_diff_enhanced'].includes(currentTool.name)" class="tool-form json-diff-tool">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="json-input-panel">
                <h4>{{ $t('dataFactory.form.jsonData1') }}</h4>
                <el-input
                  v-model="toolForm.json_str1"
                  type="textarea"
                  :rows="15"
                  :placeholder="$t('dataFactory.form.jsonData1Placeholder')"
                  @input="handleJsonDiffInput"
                />
              </div>
            </el-col>
            <el-col :span="12">
              <div class="json-input-panel">
                <h4>{{ $t('dataFactory.form.jsonData2') }}</h4>
                <el-input
                  v-model="toolForm.json_str2"
                  type="textarea"
                  :rows="15"
                  :placeholder="$t('dataFactory.form.jsonData2Placeholder')"
                  @input="handleJsonDiffInput"
                />
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" class="diff-options">
            <el-col :span="24">
              <el-form label-width="120px">
                <el-form-item :label="$t('dataFactory.form.ignoreWhitespace')">
                  <el-switch v-model="toolForm.ignore_whitespace" @change="handleJsonDiffInput" />
                </el-form-item>
                <el-form-item :label="$t('dataFactory.form.showOnlyDiff')">
                  <el-switch v-model="toolForm.show_only_diff" @change="handleJsonDiffInput" />
                </el-form-item>
              </el-form>
            </el-col>
          </el-row>
        </div>

        <!-- JSON格式化工具 - 左右分栏布局 -->
        <div v-else-if="currentCategory === 'json' && currentTool.name === 'format_json'" class="tool-form json-format-tool">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="json-input-panel">
                <div class="panel-header">
                  <h4>{{ $t('dataFactory.form.input') }}</h4>
                  <div class="input-stats">
                    <span>{{ $t('dataFactory.form.chars') }}: {{ getInputStats().chars }}</span>
                    <span>{{ $t('dataFactory.form.lines') }}: {{ getInputStats().lines }}</span>
                  </div>
                </div>
                <el-input
                  v-model="toolForm.json_str"
                  type="textarea"
                  :rows="20"
                  :placeholder="$t('dataFactory.form.jsonDataPlaceholder')"
                  @input="handleJsonInput"
                />
              </div>
            </el-col>
            <el-col :span="12">
              <div class="json-input-panel">
                <div class="panel-header">
                  <h4>{{ $t('dataFactory.form.output') }}</h4>
                  <!-- <div class="output-stats">
                    <span>字符: {{ getOutputStats().chars }}</span>
                    <span>行数: {{ getOutputStats().lines }}</span>
                  </div> -->
                </div>
                <div v-if="jsonTreeData" class="result-display json-tree-view">
                  <div class="json-tree-actions">
                    <el-button size="small" @click="expandAllJson">
                      <el-icon><Operation /></el-icon>
                      {{ $t('dataFactory.actions.expandAll') }}
                    </el-button>
                    <el-button size="small" @click="collapseAllJson">
                      <el-icon><Operation /></el-icon>
                      {{ $t('dataFactory.actions.collapseAll') }}
                    </el-button>
                  </div>
                  <el-tree
                    :data="[jsonTreeData]"
                    :props="{ label: 'label', children: 'children' }"
                    :expand-on-click-node="false"
                    :default-expand-all="false"
                    :default-expanded-keys="jsonExpandedKeys"
                    @node-expand="handleNodeExpand"
                    @node-collapse="handleNodeCollapse"
                    node-key="key"
                    class="json-tree"
                  >
                    <template #default="{ node, data }">
                      <span class="json-tree-node" :class="`json-type-${data.type}`">
                        <span class="json-node-label">{{ data.label }}</span>
                      </span>
                    </template>
                  </el-tree>
                </div>
                <div v-else-if="toolResult && toolResult.result" class="result-display">
                  <pre>{{ toolResult.result }}</pre>
                </div>
                <div v-else class="result-empty">
                  <el-empty :description="$t('dataFactory.form.formatResultEmpty')" :image-size="60" />
                </div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" class="format-options">
            <el-col :span="24">
              <div class="options-bar">
                <div class="option-group">
                  <span class="option-label">{{ $t('dataFactory.form.indent') }}:</span>
                  <el-radio-group v-model="toolForm.indent" @change="handleJsonInput">
                    <el-radio-button :value="2">{{ $t('dataFactory.form.indentSpaces2') }}</el-radio-button>
                    <el-radio-button :value="4">{{ $t('dataFactory.form.indentSpaces4') }}</el-radio-button>
                  </el-radio-group>
                </div>
                <div class="option-group">
                  <el-switch v-model="toolForm.sort_keys" @change="handleJsonInput" />
                  <span class="option-label">{{ $t('dataFactory.form.sortKeys') }}</span>
                </div>
                <div class="option-group">
                  <el-switch v-model="toolForm.compress" @change="handleJsonInput" />
                  <span class="option-label">{{ $t('dataFactory.form.compress') }}</span>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 其他JSON工具 -->
        <div v-else-if="currentCategory === 'json' && !['format_json', 'jsonpath_query', 'json_diff_enhanced'].includes(currentTool.name)" class="tool-form json-tool">
          <el-form label-width="120px">
            <el-form-item v-if="['format_json', 'validate_json', 'json_to_xml', 'json_to_yaml', 'json_to_csv', 'json_path_list', 'json_flatten'].includes(currentTool.name)" :label="$t('dataFactory.form.jsonData')">
              <el-input
                v-model="toolForm.json_str"
                type="textarea"
                :rows="8"
                :placeholder="$t('dataFactory.form.jsonDataPlaceholder')"
                @input="handleJsonInput"
              />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'format_json'" :label="$t('dataFactory.form.indent')">
              <el-input-number v-model="toolForm.indent" :min="0" :max="8" @change="handleJsonInput" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'format_json'" :label="$t('dataFactory.form.sortKeys')">
              <el-switch v-model="toolForm.sort_keys" @change="handleJsonInput" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'format_json'" :label="$t('dataFactory.form.compress')">
              <el-switch v-model="toolForm.compress" @change="handleJsonInput" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'xml_to_json'" :label="$t('dataFactory.form.xmlData')">
              <el-input v-model="toolForm.xml_str" type="textarea" :rows="8" :placeholder="$t('dataFactory.form.xmlDataPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'yaml_to_json'" :label="$t('dataFactory.form.yamlData')">
              <el-input v-model="toolForm.yaml_str" type="textarea" :rows="8" :placeholder="$t('dataFactory.form.yamlDataPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'csv_to_json'" :label="$t('dataFactory.form.csvData')">
              <el-input v-model="toolForm.csv_str" type="textarea" :rows="8" :placeholder="$t('dataFactory.form.csvDataPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'csv_to_json'" :label="$t('dataFactory.form.csvSeparator')">
              <el-input v-model="toolForm.separator" :placeholder="$t('dataFactory.form.csvSeparatorPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'csv_to_json'" :label="$t('dataFactory.form.hasHeader')">
              <el-switch v-model="toolForm.has_header" />
            </el-form-item>
          </el-form>
        </div>

        <!-- Mock数据工具 -->
        <div v-else-if="currentCategory === 'mock'" class="tool-form">
          <el-form label-width="120px">
            <el-form-item :label="$t('dataFactory.form.count')">
              <el-input-number v-model="toolForm.count" :min="1" :max="100" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_string'" :label="$t('dataFactory.form.length')">
              <el-input-number v-model="toolForm.length" :min="1" :max="100" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_string'" :label="$t('dataFactory.form.charType')">
              <el-select v-model="toolForm.char_type" :placeholder="$t('dataFactory.form.charType')">
                <el-option :label="$t('dataFactory.form.charTypeOptions.all')" value="all" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.letters')" value="letters" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.digits')" value="digits" />
                <el-option :label="$t('dataFactory.form.charTypeOptions.alphanumeric')" value="alphanumeric" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_number'" :label="$t('dataFactory.form.minValue')">
              <el-input-number v-model="toolForm.min_val" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_number'" :label="$t('dataFactory.form.maxValue')">
              <el-input-number v-model="toolForm.max_val" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_number'" :label="$t('dataFactory.form.decimals')">
              <el-input-number v-model="toolForm.decimals" :min="0" :max="10" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_date'" :label="$t('dataFactory.form.startDate')">
              <el-date-picker v-model="toolForm.start_date" type="date" :placeholder="$t('dataFactory.form.selectStartDate')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_date'" :label="$t('dataFactory.form.endDate')">
              <el-date-picker v-model="toolForm.end_date" type="date" :placeholder="$t('dataFactory.form.selectEndDate')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_datetime'" :label="$t('dataFactory.form.startDate')">
              <el-date-picker v-model="toolForm.start_date" type="datetime" :placeholder="$t('dataFactory.form.selectStartDateTime')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'mock_datetime'" :label="$t('dataFactory.form.endDate')">
              <el-date-picker v-model="toolForm.end_date" type="datetime" :placeholder="$t('dataFactory.form.selectEndDateTime')" />
            </el-form-item>
          </el-form>
        </div>

        <!-- Crontab工具 -->
        <div v-else-if="currentCategory === 'crontab'" class="tool-form">
          <el-form label-width="120px">
            <el-form-item v-if="currentTool.name === 'generate_expression'" :label="$t('dataFactory.form.minute')">
              <el-input v-model="toolForm.minute" placeholder="0-59, *, */5, 1,3,5, 1-10" />
              <span class="form-tip">{{ $t('dataFactory.form.minuteTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_expression'" :label="$t('dataFactory.form.hour')">
              <el-input v-model="toolForm.hour" placeholder="0-23, *, */2, 9,18, 8-18" />
              <span class="form-tip">{{ $t('dataFactory.form.hourTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_expression'" :label="$t('dataFactory.form.day')">
              <el-input v-model="toolForm.day" placeholder="1-31, *, */7, 1,15, 1-10" />
              <span class="form-tip">{{ $t('dataFactory.form.dayTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_expression'" :label="$t('dataFactory.form.month')">
              <el-input v-model="toolForm.month" placeholder="1-12, *, */3, 1,4,7,10, 6-9" />
              <span class="form-tip">{{ $t('dataFactory.form.monthTip') }}</span>
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'generate_expression'" :label="$t('dataFactory.form.weekday')">
              <el-input v-model="toolForm.weekday" placeholder="0-6, *, */2, 1-5, 1,3,5" />
              <span class="form-tip">{{ $t('dataFactory.form.weekdayTip') }}</span>
            </el-form-item>
            <el-form-item v-if="['parse_expression', 'get_next_runs', 'validate_expression'].includes(currentTool.name)" :label="$t('dataFactory.form.crontabExpression')">
              <el-input v-model="toolForm.expression" type="textarea" :rows="3" :placeholder="$t('dataFactory.form.crontabExpressionPlaceholder')" />
            </el-form-item>
            <el-form-item v-if="currentTool.name === 'get_next_runs'" :label="$t('dataFactory.form.runCount')">
              <el-input-number v-model="toolForm.count" :min="1" :max="20" />
            </el-form-item>
          </el-form>
        </div>

        <el-form label-width="120px" class="tool-options">
          <el-form-item :label="$t('dataFactory.form.saveResult')">
            <el-switch v-model="toolForm.isSaved" />
            <span class="form-tip">{{ $t('dataFactory.form.saveResultTip') }}</span>
          </el-form-item>
          <el-form-item :label="$t('dataFactory.form.tags')">
            <el-input
              v-model="toolForm.tags"
              :placeholder="$t('dataFactory.form.tagsPlaceholder')"
            />
          </el-form-item>
        </el-form>

        <div v-if="toolResult && currentTool?.name !== 'jsonpath_query' && currentTool?.name !== 'format_json'" class="tool-result">
          <div class="result-header">
            <h4>{{ $t('dataFactory.form.result') }}</h4>
            <el-button
              v-if="['json_to_xml', 'json_to_yaml', 'json_to_csv', 'xml_to_json', 'yaml_to_json', 'csv_to_json'].includes(currentTool?.name)"
              type="primary"
              size="small"
              @click="downloadResult"
            >
              <el-icon><Download /></el-icon>
              {{ $t('dataFactory.actions.download') }}
            </el-button>
          </div>
          <div v-if="['generate_barcode', 'generate_qrcode', 'base64_to_image'].includes(currentTool?.name)" class="image-result">
            <div class="image-preview">
              <img v-if="toolResult.url" :src="getImageUrl(toolResult.url)" :alt="currentTool.display_name" />
              <div v-else class="no-image">{{ $t('dataFactory.image.generateFailed') }}</div>
            </div>
            <div class="image-actions">
              <el-button type="primary" @click="downloadImage(toolResult)">
                <el-icon><Download /></el-icon>
                {{ $t('dataFactory.actions.downloadImage') }}
              </el-button>
              <el-tag v-if="toolResult.filename" type="info">{{ toolResult.filename }}</el-tag>
            </div>
          </div>
          <el-input
            v-else-if="typeof toolResult === 'string'"
            v-model="toolResult"
            type="textarea"
            :rows="6"
            readonly
          />
          <pre v-else>{{ JSON.stringify(toolResult, null, 2) }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button @click="toolDialogVisible = false">{{ $t('dataFactory.actions.cancel') }}</el-button>
        <el-button type="primary" :loading="executing" @click="executeTool">
          {{ $t('dataFactory.actions.execute') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 历史记录对话框 -->
    <el-dialog
      v-model="showHistory"
      :title="$t('dataFactory.history.title')"
      width="1200px"
    >
      <el-tabs v-model="historyTab">
        <el-tab-pane :label="$t('dataFactory.history.allRecords')" name="all">
          <div class="history-content">
            <el-table :data="historyRecords" stripe class="history-table">
              <el-table-column :label="$t('dataFactory.history.toolName')" min-width="180">
                <template #default="{ row }">
                  <span>{{ getToolDisplayName(row.tool_name) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="tool_category_display" :label="$t('dataFactory.history.category')" min-width="120" />
              <el-table-column prop="tool_scenario_display" :label="$t('dataFactory.history.scenario')" min-width="120" />
              <el-table-column :label="$t('dataFactory.history.usageTime')" min-width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column :label="$t('dataFactory.history.operation')" width="100" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" type="danger" @click="deleteRecord(row)">{{ $t('dataFactory.actions.delete') }}</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="historyCurrentPage"
              v-model:page-size="historyPageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="historyTotal"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleHistorySizeChange"
              @current-change="handleHistoryPageChange"
              class="history-pagination"
            />
          </div>
        </el-tab-pane>
        <el-tab-pane :label="$t('dataFactory.history.statistics')" name="stats">
          <div class="stats-container">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-card class="total-stats-card">
                  <div class="total-stats">
                    <div class="total-stat-item">
                      <div class="total-stat-value">{{ statistics.total_records || 0 }}</div>
                      <div class="total-stat-label">{{ $t('dataFactory.history.totalRecords') }}</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            <el-row :gutter="20" style="margin-top: 20px;">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span class="card-header-title">{{ $t('dataFactory.history.categoryStats') }}</span>
                  </template>
                  <div v-if="statistics.category_stats && Object.keys(statistics.category_stats).length > 0">
                    <div v-for="(count, category) in statistics.category_stats" :key="category" class="stat-item">
                      <div class="stat-item-content">
                        <span class="stat-label">{{ category }}</span>
                        <el-progress 
                          :percentage="calculatePercentage(count, statistics.total_records)" 
                          :stroke-width="12"
                          :show-text="false"
                        />
                        <span class="stat-count">{{ count }}</span>
                      </div>
                    </div>
                  </div>
                  <el-empty v-else :description="$t('dataFactory.history.noData')" :image-size="80" />
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span class="card-header-title">{{ $t('dataFactory.history.scenarioStats') }}</span>
                  </template>
                  <div v-if="statistics.scenario_stats && Object.keys(statistics.scenario_stats).length > 0">
                    <div v-for="(count, scenario) in statistics.scenario_stats" :key="scenario" class="stat-item">
                      <div class="stat-item-content">
                        <span class="stat-label">{{ scenario }}</span>
                        <el-progress 
                          :percentage="calculatePercentage(count, statistics.total_records)" 
                          :stroke-width="12"
                          :show-text="false"
                        />
                        <span class="stat-count">{{ count }}</span>
                      </div>
                    </div>
                  </div>
                  <el-empty v-else :description="$t('dataFactory.history.noData')" :image-size="80" />
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  DataLine, Menu, Grid, Clock, Operation, ArrowRight,
  Document, List, Lock, User, MagicStick, VideoPlay, ChatDotSquare, Picture, Connection,
  Phone, Message, Location, Ticket, OfficeBuilding, CreditCard, CircleCheck, DocumentCopy, Search, Delete, Edit, Unlock, DataLine as DataLineIcon, Sort, Share, View, Upload
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const { t } = useI18n()

const viewMode = ref('category')
const categories = ref([])
const scenarios = ref([])
const currentScenario = ref(null)
const toolDialogVisible = ref(false)
const currentTool = ref(null)
const currentCategory = ref('')
const toolForm = ref({
  count: 1,
  text: '',
  isSaved: false,
  tags: '',
  gender: 'random',
  region: 'all',
  domain: 'random',
  full_address: true,
  company_type: 'all',
  old_str: '',
  new_str: '',
  is_regex: false,
  escape_type: 'json',
  unescape_type: 'json',
  pattern: '',
  flags: [],
  text1: '',
  text2: '',
  convert_type: 'to_ascii',
  format_type: 'trim',
  min_val: 1,
  max_val: 100,
  precision: 2,
  length: 8,
  char_type: 'all',
  version: 4,
  separator: ':',
  ip_version: 4,
  start_date: '2025-01-01',
  end_date: '2025-12-31',
  date_format: '%Y-%m-%d',
  format: 'hex',
  char_options: ['include_uppercase', 'include_lowercase', 'include_digits', 'include_special'],
  data: '',
  barcode_type: 'code128',
  timestamp: '',
  timestamp_convert_type: 'to_datetime',
  timestamp_unit: 'auto',
  number: '',
  from_base: 10,
  to_base: 16,
  from_type: 'hex',
  to_type: 'rgb',
  encoding: 'utf-8',
  unicode_convert_type: 'to_unicode',
  hash_value: '',
  algorithm: 'md5',
  password: '',
  mode: 'CBC',
  json_str: '',
  json_str1: '',
  json_str2: '',
  xml_str: '',
  yaml_str: '',
  csv_str: '',
  jsonpath_expr: '',
  root_tag: 'root',
  indent: 2,
  sort_keys: false,
  compress: false,
  ignore_whitespace: true,
  has_header: true,
  show_only_diff: false,
  array_length: 5,
  item_type: 'string',
  keys: '',
  value_type: 'string',
  plus: false,
  token: '',
  verify: false,
  secret: '',
  minute: '*',
  hour: '*',
  day: '*',
  month: '*',
  weekday: '*',
  expression: '',
  image_data: '',
  image_format: 'png',
  include_prefix: true,
  base64_str: ''
})
const toolResult = ref(null)
const imagePreview = ref('')
const qrCodeImage = ref('')
const uploadRef = ref(null)
const executing = ref(false)
const showHistory = ref(false)
const historyTab = ref('all')
const historyRecords = ref([])
const historyTotal = ref(0)
const historyCurrentPage = ref(1)
const historyPageSize = ref(10)
const statistics = ref({})
const jsonTreeData = ref(null)
const jsonExpandedKeys = ref([])
const jsonCollapseState = ref({})

const iconMap = {
  'document': Document,
  'code': List,
  'distribute': Grid,
  'lock': Lock,
  'user': User,
  'magic': MagicStick,
  'video': VideoPlay,
  'chat': ChatDotSquare,
  'clock': Clock,
  'picture': Picture,
  'phone': Phone,
  'message': Message,
  'location': Location,
  'ticket': Ticket,
  'office': OfficeBuilding,
  'credit-card': CreditCard,
  'circle-check': CircleCheck,
  'document-copy': DocumentCopy,
  'search': Search,
  'delete': Delete,
  'edit': Edit,
  'unlock': Unlock,
  'data-line': DataLineIcon,
  'sort': Sort,
  'share': Share,
  'view': View
}

const getIcon = (iconName) => {
  return iconMap[iconName] || Operation
}

const getScenarioIcon = (scenario) => {
  const iconMapping = {
    'test_data': User,
    'json': List,
    'string': Document,
    'encoding': Connection,
    'random': MagicStick,
    'encryption': Lock,
    'crontab': Clock
  }
  return iconMapping[scenario] || Operation
}

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/data-factory/categories/')
    categories.value = response.data.categories
  } catch (error) {
    ElMessage.error(t('dataFactory.messages.fetchCategoriesFailed'))
  }
}

const fetchScenarios = async () => {
  try {
    const response = await axios.get('/api/data-factory/categories/')
    const scenarioMap = {}
    response.data.categories.forEach(category => {
      category.tools.forEach(tool => {
        const scenario = tool.scenario || 'other'
        if (!scenarioMap[scenario]) {
          scenarioMap[scenario] = {
            scenario: scenario,
            name: getScenarioName(scenario),
            description: getScenarioDesc(scenario),
            tool_count: 0
          }
        }
        scenarioMap[scenario].tool_count++
      })
    })
    scenarios.value = Object.values(scenarioMap)
  } catch (error) {
    ElMessage.error(t('dataFactory.messages.fetchScenariosFailed'))
  }
}

const getScenarioName = (scenario) => {
  const key = `dataFactory.scenarios.${scenario}`
  const translated = t(key)
  // vue-i18n returns the key itself if translation doesn't exist
  return translated === key ? t('dataFactory.scenarios.other') : translated
}

const getScenarioDesc = (scenario) => {
  const key = `dataFactory.scenarioDescs.${scenario}`
  const translated = t(key)
  return translated === key ? t('dataFactory.scenarioDescs.other') : translated
}

const getCategoryName = (category) => {
  const key = `dataFactory.scenarios.${category}`
  const translated = t(key)
  return translated === key ? category : translated
}

const getToolDisplayName = (toolName) => {
  const key = `dataFactory.tools.${toolName}`
  const translated = t(key)
  // vue-i18n returns the key itself if translation doesn't exist
  return translated === key ? null : translated
}

const getToolDescription = (toolName) => {
  const key = `dataFactory.toolDescs.${toolName}`
  const translated = t(key)
  return translated === key ? null : translated
}

const goToHome = () => {
  router.push('/')
}

const openTool = (tool, category) => {
  currentTool.value = tool
  currentCategory.value = category
  toolDialogVisible.value = true
  resetToolForm()
}

const buildInputData = () => {
  const toolName = currentTool.value.name
  const category = currentCategory.value
  const form = toolForm.value

  if (category === 'test_data') {
    const data = { count: form.count }
    if (toolName === 'generate_chinese_name') data.gender = form.gender
    if (toolName === 'generate_chinese_phone') data.region = form.region
    if (toolName === 'generate_chinese_email') data.domain = form.domain
    if (toolName === 'generate_chinese_address') data.full_address = form.full_address
    if (toolName === 'generate_company_name') data.company_type = form.company_type
    return data
  }

  if (category === 'string') {
    if (toolName === 'remove_whitespace') return { text: form.text }
    if (toolName === 'replace_string') return { text: form.text, old_str: form.old_str, new_str: form.new_str, is_regex: form.is_regex }
    if (toolName === 'escape_string') return { text: form.text, escape_type: form.escape_type }
    if (toolName === 'unescape_string') return { text: form.text, unescape_type: form.unescape_type }
    if (toolName === 'word_count') return { text: form.text }
    if (toolName === 'text_diff') return { text1: form.text1, text2: form.text2 }
    if (toolName === 'regex_test') return { pattern: form.pattern, text: form.text, flags: form.flags.join('') }
    if (toolName === 'case_convert') return { text: form.text, convert_type: form.convert_type }
    if (toolName === 'string_format') return { text: form.text, format_type: form.format_type }
  }

  if (category === 'random') {
    if (toolName === 'random_int') return { min_val: form.min_val, max_val: form.max_val, count: form.count }
    if (toolName === 'random_float') return { min_val: form.min_val, max_val: form.max_val, precision: form.precision, count: form.count }
    if (toolName === 'random_string') return { length: form.length, char_type: form.char_type, count: form.count }
    if (toolName === 'random_uuid') return { version: form.version, count: form.count }
    if (toolName === 'random_mac_address') return { separator: form.separator, count: form.count }
    if (toolName === 'random_ip_address') return { ip_version: form.ip_version, count: form.count }
    if (toolName === 'random_date') {
      const formatDate = (date) => {
        if (!date) return ''
        const d = new Date(date)
        const year = d.getFullYear()
        const month = String(d.getMonth() + 1).padStart(2, '0')
        const day = String(d.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
      }
      return { start_date: formatDate(form.start_date), end_date: formatDate(form.end_date), count: form.count, date_format: form.date_format }
    }
    if (toolName === 'random_boolean') return { count: form.count }
    if (toolName === 'random_color') return { format: form.format, count: form.count }
    if (toolName === 'random_password') {
      return {
        length: form.length,
        include_uppercase: form.char_options.includes('include_uppercase'),
        include_lowercase: form.char_options.includes('include_lowercase'),
        include_digits: form.char_options.includes('include_digits'),
        include_special: form.char_options.includes('include_special'),
        count: form.count
      }
    }
    if (toolName === 'random_sequence') {
      const sequence = form.sequence ? form.sequence.split(',').map(s => s.trim()) : []
      return { sequence: sequence, count: form.count, unique: form.unique }
    }
  }

  if (category === 'encoding') {
    if (toolName === 'generate_barcode') return { data: form.data, barcode_type: form.barcode_type }
    if (toolName === 'generate_qrcode') return { data: form.data, image_size: form.image_size, border: 4 }
    if (toolName === 'decode_qrcode') return { image_data: form.image_data || '', image_format: 'png' }
    if (toolName === 'timestamp_convert') return { timestamp: form.timestamp, convert_type: form.timestamp_convert_type, timestamp_unit: form.timestamp_unit }
    if (toolName === 'base_convert') return { number: form.number, from_base: form.from_base, to_base: form.to_base }
    if (toolName === 'unicode_convert') return { text: form.text, convert_type: form.unicode_convert_type }
    if (toolName === 'ascii_convert') return { text: form.text, convert_type: form.convert_type }
    if (toolName === 'color_convert') return { color: form.color, from_type: form.from_type, to_type: form.to_type }
    if (toolName === 'url_encode') return { data: form.data, encoding: form.encoding, plus: form.plus }
    if (toolName === 'url_decode') return { data: form.data, encoding: form.encoding, plus: form.plus }
    if (toolName === 'jwt_decode') return { token: form.token, verify: form.verify, secret: form.secret }
    if (toolName === 'image_to_base64') return { image_data: form.image_data || '', image_format: form.image_format || 'png', include_prefix: form.include_prefix !== false }
    if (toolName === 'base64_to_image') return { base64_str: form.base64_str || '' }
    if (toolName === 'base64_encode') return { text: form.text, encoding: form.encoding }
    if (toolName === 'base64_decode') return { text: form.text, encoding: form.encoding }
  }

  if (category === 'encryption') {
    if (toolName === 'md5_hash') return { text: form.text }
    if (toolName === 'sha1_hash') return { text: form.text }
    if (toolName === 'sha256_hash') return { text: form.text }
    if (toolName === 'sha512_hash') return { text: form.text }
    if (toolName === 'hash_comparison') return { text: form.text, hash_value: form.hash_value, algorithm: form.algorithm }
    if (toolName === 'aes_encrypt') return { text: form.text, password: form.password, mode: form.mode }
    if (toolName === 'aes_decrypt') return { encrypted_text: form.text, password: form.password, mode: form.mode }
    if (toolName === 'password_strength') return { password: form.text }
    if (toolName === 'generate_salt') return { length: form.length }
  }

  if (category === 'json') {
    if (toolName === 'format_json') return { json_str: form.json_str, indent: form.indent, sort_keys: form.sort_keys, compress: form.compress }
    if (toolName === 'validate_json') return { json_str: form.json_str }
    if (toolName === 'json_to_xml') return { json_str: form.json_str, root_tag: form.root_tag || 'root' }
    if (toolName === 'xml_to_json') return { xml_str: form.xml_str }
    if (toolName === 'json_to_yaml') return { json_str: form.json_str }
    if (toolName === 'yaml_to_json') return { yaml_str: form.yaml_str }
    if (toolName === 'json_diff_enhanced') return { json_str1: form.json_str1, json_str2: form.json_str2, ignore_whitespace: form.ignore_whitespace, show_only_diff: form.show_only_diff }
    if (toolName === 'jsonpath_query') return { json_str: form.json_str, jsonpath_expr: form.jsonpath_expr }
    if (toolName === 'json_path_list') return { json_str: form.json_str }
    if (toolName === 'json_flatten') return { json_str: form.json_str, separator: form.separator || '.' }
  }

  if (category === 'crontab') {
    if (toolName === 'generate_expression') return { minute: form.minute || '*', hour: form.hour || '*', day: form.day || '*', month: form.month || '*', weekday: form.weekday || '*' }
    if (toolName === 'parse_expression') return { expression: form.expression || '' }
    if (toolName === 'get_next_runs') return { expression: form.expression || '', count: form.count || 10 }
    if (toolName === 'validate_expression') return { expression: form.expression || '' }
  }

  if (category === 'mock') {
    const data = { count: form.count }
    if (toolName === 'mock_string') {
      data.length = form.length
      data.char_type = form.char_type
    }
    if (toolName === 'mock_number') {
      data.min_val = form.min_val
      data.max_val = form.max_val
      data.decimals = form.decimals
    }
    if (toolName === 'mock_date' || toolName === 'mock_datetime') {
      data.start_date = form.start_date
      data.end_date = form.end_date
    }
    if (toolName === 'mock_array') {
      data.array_length = form.array_length
      data.item_type = form.item_type
    }
    if (toolName === 'mock_object') {
      data.keys = form.keys ? form.keys.split(',').map(k => k.trim()) : ['id', 'name', 'value']
      data.value_type = form.value_type
    }
    return data
  }

  return {}
}

const executeTool = async () => {
  if (!currentTool.value) return

  executing.value = true
  try {
    const input_data = buildInputData()
    const response = await axios.post('/api/data-factory/', {
      tool_name: currentTool.value.name,
      tool_category: currentCategory.value,
      tool_scenario: currentTool.value.scenario || 'other',
      input_data: input_data,
      is_saved: toolForm.value.isSaved,
      tags: toolForm.value.tags ? toolForm.value.tags.split(',') : []
    })

    toolResult.value = response.data
    ElMessage.success(t('dataFactory.messages.executeSuccess'))
  } catch (error) {
    ElMessage.error(error.response?.data?.error || t('dataFactory.messages.executeFailed'))
  } finally {
    executing.value = false
  }
}

const resetToolForm = () => {
  toolForm.value = {
    count: 1,
    text: '',
    isSaved: false,
    tags: '',
    gender: 'random',
    region: 'all',
    domain: 'random',
    full_address: true,
    company_type: 'all',
    old_str: '',
    new_str: '',
    is_regex: false,
    escape_type: 'json',
    unescape_type: 'json',
    pattern: '',
    flags: [],
    text1: '',
    text2: '',
    convert_type: 'to_ascii',
    format_type: 'trim',
    min_val: 1,
    max_val: 100,
    precision: 2,
    length: 8,
    char_type: 'all',
    image_size: 300,
    separator: ':',
    ip_version: 4,
    start_date: '2025-01-01',
    end_date: '2025-12-31',
    date_format: '%Y-%m-%d',
    format: 'hex',
    char_options: ['include_uppercase', 'include_lowercase', 'include_digits', 'include_special'],
    data: '',
    barcode_type: 'code128',
    timestamp: '',
    timestamp_convert_type: 'to_datetime',
    timestamp_unit: 'auto',
    number: '',
    from_base: 10,
    to_base: 16,
    from_type: 'hex',
    to_type: 'rgb',
    encoding: 'utf-8',
    unicode_convert_type: 'to_unicode',
    hash_value: '',
    algorithm: 'md5',
    password: '',
    mode: 'CBC',
    json_str: '',
    json_str1: '',
    json_str2: '',
    xml_str: '',
    yaml_str: '',
    csv_str: '',
    jsonpath_expr: '',
    root_tag: 'root',
    indent: 2,
    sort_keys: false,
    compress: false,
    ignore_whitespace: true,
    has_header: true,
    show_only_diff: false,
    array_length: 5,
    item_type: 'string',
    keys: '',
    value_type: 'string',
    minute: '*',
    hour: '*',
    day: '*',
    month: '*',
    weekday: '*',
    expression: '',
    image_data: '',
    image_format: 'png',
    include_prefix: true,
    base64_str: '',
    sequence: '',
    unique: false
  }
  toolResult.value = null
  imagePreview.value = ''
  jsonTreeData.value = null
  jsonExpandedKeys.value = []
  jsonCollapseState.value = {}
}

let debounceTimer = null
const handleJsonInput = async () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  
  debounceTimer = setTimeout(async () => {
    if (currentTool.value?.name === 'format_json' && toolForm.value.json_str) {
      try {
        const response = await axios.post('/api/data-factory/', {
          tool_name: 'format_json',
          tool_category: 'json',
          tool_scenario: 'data_validation',
          input_data: {
            json_str: toolForm.value.json_str,
            indent: toolForm.value.indent,
            sort_keys: toolForm.value.sort_keys,
            compress: toolForm.value.compress
          },
          is_saved: false
        })
        toolResult.value = response.data
        jsonTreeData.value = parseJsonToTree(response.data.result)
        saveJsonCollapseState()
      } catch (error) {
        toolResult.value = null
        jsonTreeData.value = null
      }
    }
  }, 300)
}

const parseJsonToTree = (jsonStr) => {
  try {
    const obj = JSON.parse(jsonStr)
    return convertObjectToTree(obj)
  } catch (e) {
    return null
  }
}

const convertObjectToTree = (obj, key = 'root', path = '') => {
  const currentPath = path ? `${path}.${key}` : key
  
  if (obj === null) {
    return {
      key: currentPath,
      label: `${key}: null`,
      value: null,
      type: 'null',
      children: []
    }
  }
  
  if (typeof obj === 'object') {
    const isArray = Array.isArray(obj)
    const children = Object.keys(obj).map(k => convertObjectToTree(obj[k], k, currentPath))
    
    return {
      key: currentPath,
      label: `${key}${isArray ? ` [${obj.length}]` : ''}`,
      value: isArray ? `Array(${obj.length})` : `Object{${Object.keys(obj).length}}`,
      type: isArray ? 'array' : 'object',
      children: children
    }
  }
  
  const type = typeof obj
  return {
    key: currentPath,
    label: `${key}: ${String(obj)}`,
    value: String(obj),
    type: type,
    children: []
  }
}

const expandAllJson = () => {
  const getAllKeys = (nodes) => {
    let keys = []
    nodes.forEach(node => {
      keys.push(node.key)
      if (node.children && node.children.length > 0) {
        keys = keys.concat(getAllKeys(node.children))
      }
    })
    return keys
  }
  
  if (jsonTreeData.value) {
    jsonExpandedKeys.value = getAllKeys([jsonTreeData.value])
    saveJsonCollapseState()
  }
}

const collapseAllJson = () => {
  jsonExpandedKeys.value = []
  saveJsonCollapseState()
}

const saveJsonCollapseState = () => {
  if (currentTool.value?.name === 'format_json') {
    const state = {
      expandedKeys: jsonExpandedKeys.value,
      timestamp: Date.now()
    }
    localStorage.setItem('json_format_collapse_state', JSON.stringify(state))
  }
}

const loadJsonCollapseState = () => {
  try {
    const state = localStorage.getItem('json_format_collapse_state')
    if (state) {
      const parsed = JSON.parse(state)
      jsonExpandedKeys.value = parsed.expandedKeys || []
    }
  } catch (e) {
    jsonExpandedKeys.value = []
  }
}

watch(() => currentTool.value, (newTool) => {
  if (newTool?.name === 'format_json') {
    loadJsonCollapseState()
  }
  if (newTool?.name !== 'decode_qrcode') {
    qrCodeImage.value = ''
    toolForm.value.image_data = ''
  }
})

const handleNodeExpand = (data, node) => {
  if (!jsonExpandedKeys.value.includes(data.key)) {
    jsonExpandedKeys.value.push(data.key)
    saveJsonCollapseState()
  }
}

const handleNodeCollapse = (data, node) => {
  const index = jsonExpandedKeys.value.indexOf(data.key)
  if (index > -1) {
    jsonExpandedKeys.value.splice(index, 1)
    saveJsonCollapseState()
  }
}

const handleQrCodeUpload = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64Data = e.target.result
      qrCodeImage.value = base64Data
      toolForm.value.image_data = base64Data
      resolve(false)
    }
    reader.onerror = () => {
      ElMessage.error(t('dataFactory.messages.imageReadFailed'))
      reject(false)
    }
    reader.readAsDataURL(file)
  })
}

const clearQrCodeImage = () => {
  qrCodeImage.value = ''
  toolForm.value.image_data = ''
}

const getInputStats = () => {
  const text = toolForm.value.json_str || ''
  return {
    chars: text.length,
    lines: text.split('\n').length
  }
}

const getOutputStats = () => {
  if (!toolResult.value || !toolResult.value.result) {
    return { chars: 0, lines: 0 }
  }
  const text = toolResult.value.result
  return {
    chars: text.length,
    lines: text.split('\n').length
  }
}

const handleJsonDiffInput = async () => {
  if (currentTool.value?.name === 'json_diff_enhanced') {
    if (!toolForm.value.json_str1 || !toolForm.value.json_str2) {
      toolResult.value = null
      return
    }
    try {
      const response = await axios.post('/api/data-factory/', {
        tool_name: 'json_diff_enhanced',
        tool_category: 'json',
        tool_scenario: 'data_validation',
        input_data: {
          json_str1: toolForm.value.json_str1,
          json_str2: toolForm.value.json_str2,
          ignore_whitespace: toolForm.value.ignore_whitespace,
          show_only_diff: toolForm.value.show_only_diff
        },
        is_saved: false
      })
      toolResult.value = response.data
    } catch (error) {
      toolResult.value = null
    }
  }
}

const handleJsonPathInput = async () => {
  if (currentTool.value?.name === 'jsonpath_query' && toolForm.value.json_str && toolForm.value.jsonpath_expr) {
    try {
      const response = await axios.post('/api/data-factory/', {
        tool_name: 'jsonpath_query',
        tool_category: 'json',
        tool_scenario: 'data_validation',
        input_data: {
          json_str: toolForm.value.json_str,
          jsonpath_expr: toolForm.value.jsonpath_expr
        },
        is_saved: false
      })
      toolResult.value = response.data
    } catch (error) {
      toolResult.value = null
    }
  }
}

const handleImageChange = (file) => {
  if (file.raw.size > 10 * 1024 * 1024) {
    ElMessage.error(t('dataFactory.messages.fileSizeLimit'))
    return false
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)

  const fileReader = new FileReader()
  fileReader.onload = (e) => {
    const result = e.target.result
    if (result.startsWith('data:image')) {
      toolForm.value.image_data = result.split(',')[1]
    } else {
      toolForm.value.image_data = result
    }
  }
  fileReader.readAsDataURL(file.raw)
}

const downloadResult = () => {
  if (!toolResult.value) return

  let content = ''
  let filename = ''
  let mimeType = 'text/plain'

  const toolName = currentTool.value?.name

  if (toolName === 'json_to_xml') {
    content = toolResult.value.result || toolResult.value
    filename = `${toolName}_${Date.now()}.xml`
    mimeType = 'application/xml'
  } else if (toolName === 'xml_to_json') {
    content = toolResult.value.result || toolResult.value
    filename = `${toolName}_${Date.now()}.json`
    mimeType = 'application/json'
  } else if (toolName === 'json_to_yaml') {
    content = toolResult.value.result || toolResult.value
    filename = `${toolName}_${Date.now()}.yaml`
    mimeType = 'text/yaml'
  } else if (toolName === 'yaml_to_json') {
    content = toolResult.value.result || toolResult.value
    filename = `${toolName}_${Date.now()}.json`
    mimeType = 'application/json'
  } else if (toolName === 'json_to_csv') {
    content = toolResult.value.result || toolResult.value
    filename = `${toolName}_${Date.now()}.csv`
    mimeType = 'text/csv;charset=utf-8'
    content = '\ufeff' + content
  } else if (toolName === 'csv_to_json') {
    content = toolResult.value.result || toolResult.value
    filename = `${toolName}_${Date.now()}.csv`
    mimeType = 'text/csv;charset=utf-8'
    content = '\ufeff' + content
  } else {
    content = typeof toolResult.value === 'string' ? toolResult.value : JSON.stringify(toolResult.value, null, 2)
    filename = `${toolName}_${Date.now()}.json`
    mimeType = 'application/json'
  }

  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const filterByScenario = (scenario) => {
  currentScenario.value = scenario
  viewMode.value = 'category'
  ElMessage.success(`${t('dataFactory.messages.filtered')}: ${scenario.name}`)
}

const clearScenario = () => {
  currentScenario.value = null
}

const filteredCategories = () => {
  if (!currentScenario.value) return categories.value
  return categories.value.map(category => ({
    ...category,
    tools: category.tools.filter(tool => tool.scenario === currentScenario.value.scenario)
  })).filter(category => category.tools.length > 0)
}

const fetchHistory = async () => {
  try {
    const response = await axios.get('/api/data-factory/', {
      params: {
        page: historyCurrentPage.value,
        page_size: historyPageSize.value
      }
    })
    historyRecords.value = response.data.results
    historyTotal.value = response.data.count
  } catch (error) {
    ElMessage.error(t('dataFactory.messages.fetchHistoryFailed'))
  }
}

const handleHistoryPageChange = (page) => {
  historyCurrentPage.value = page
  fetchHistory()
}

const handleHistorySizeChange = (size) => {
  historyPageSize.value = size
  historyCurrentPage.value = 1
  fetchHistory()
}

const fetchStatistics = async () => {
  try {
    const response = await axios.get('/api/data-factory/statistics/')
    statistics.value = response.data
  } catch (error) {
    ElMessage.error(t('dataFactory.messages.fetchStatsFailed'))
  }
}

const deleteRecord = async (record) => {
  try {
    await axios.delete(`/api/data-factory/${record.id}/`)
    ElMessage.success(t('dataFactory.history.deleteSuccess'))
    fetchHistory()
    fetchStatistics()
  } catch (error) {
    ElMessage.error(t('dataFactory.history.deleteFailed'))
  }
}

const calculatePercentage = (value, total) => {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `/api/data-factory/download_static_file/?filename=${url.split('/').pop()}`
}

const downloadImage = (result) => {
  if (!result || !result.url) {
    ElMessage.error(t('dataFactory.messages.imageUrlNotFound'))
    return
  }
  
  const link = document.createElement('a')
  const filename = result.url.split('/').pop()
  const downloadUrl = `/api/data-factory/download_static_file/?filename=${filename}`
  link.href = downloadUrl
  link.download = result.filename || 'image.png'
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success(t('dataFactory.messages.downloadStarted'))
}

watch(showHistory, (newVal) => {
  if (newVal) {
    fetchHistory()
    fetchStatistics()
  }
})

watch(historyTab, (newVal) => {
  if (newVal === 'stats') {
    fetchStatistics()
  }
})

onMounted(() => {
  fetchCategories()
  fetchScenarios()
})
</script>

<style scoped lang="scss">
.data-factory-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
}

.header-card {
  margin-bottom: 20px;

  .header-content {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .page-title {
    font-size: 28px;
    font-weight: 600;
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0;
    cursor: pointer;
    transition: color 0.3s;

    &:hover {
      color: #409eff;
    }

    .title-icon {
      font-size: 32px;
      color: #409eff;
    }
  }

  .page-subtitle {
    font-size: 16px;
    color: #7f8c8d;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
  }
}

.category-view {
  display: flex;
  flex-direction: column;
  gap: 20px;

  .category-section {
    .category-card {
      .category-header {
        display: flex;
        align-items: center;
        gap: 10px;

        .category-icon {
          font-size: 24px;
        }

        .category-title {
          flex: 1;
          font-size: 18px;
          font-weight: 600;
        }
      }

      .tools-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 15px;
        margin-top: 15px;
      }

      .tool-item {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        cursor: pointer;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        gap: 12px;

        &:hover {
          background: #fff;
          border-color: #409eff;
          box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
          transform: translateY(-2px);
        }

        .tool-icon {
          width: 40px;
          height: 40px;
          background: #e6f7ff;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #409eff;
          font-size: 20px;
        }

        .tool-info {
          flex: 1;

          .tool-name {
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 5px 0;
            color: #2c3e50;
          }

          .tool-desc {
            font-size: 12px;
            color: #7f8c8d;
            margin: 0;
            line-height: 1.4;
          }
        }

        .tool-arrow {
          color: #c0c4cc;
          transition: transform 0.3s;
        }

        &:hover .tool-arrow {
          transform: translateX(5px);
          color: #409eff;
        }
      }
    }
  }
}

.scenario-view {
  .scenario-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transform: translateY(-5px);
    }

    .scenario-content {
      text-align: center;
      padding: 20px;

      .scenario-icon {
        font-size: 48px;
        color: #409eff;
        margin-bottom: 15px;
      }

      .scenario-title {
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 10px 0;
        color: #2c3e50;
      }

      .scenario-desc {
        font-size: 14px;
        color: #7f8c8d;
        margin: 0 0 15px 0;
        line-height: 1.5;
      }

      .scenario-stats {
        display: flex;
        justify-content: center;
      }
    }
  }
}

.tool-execution {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding-right: 10px;

  .tool-alert {
    margin-bottom: 20px;
  }

  .tool-form {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;

    .form-tip {
      margin-left: 10px;
      font-size: 12px;
      color: #909399;
    }
  }

  .tool-options {
    margin-bottom: 20px;

    .form-tip {
      margin-left: 10px;
      font-size: 12px;
      color: #909399;
    }
  }

  .tool-result {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 15px;

    h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      font-weight: 600;
      color: #2c3e50;
    }

    pre {
      margin: 0;
      padding: 10px;
      background: #fff;
      border-radius: 4px;
      overflow-x: auto;
      max-height: 400px;
      overflow-y: auto;
    }

    .image-result {
      display: flex;
      flex-direction: column;
      gap: 15px;

      .image-preview {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        background: #fff;
        border-radius: 8px;
        border: 2px dashed #dcdfe6;
        min-height: 200px;

        img {
          max-width: 100%;
          max-height: 400px;
          border-radius: 4px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .no-image {
          color: #909399;
          font-size: 14px;
        }
      }

      .image-actions {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        padding: 10px;
        background: #fff;
        border-radius: 8px;
      }
    }
  }
}

.history-table {
  :deep(.el-table) {
    .el-table__cell {
      text-align: center;
    }
    
    .el-table__header-wrapper {
      .el-table__header {
        th {
          text-align: center;
          background-color: #f5f7fa;
        }
      }
    }
  }
}

.history-content {
  max-height: calc(100vh - 300px);
  display: flex;
  flex-direction: column;

  .history-table {
    flex: 1;
    overflow-y: auto;

    :deep(.el-table) {
      overflow: visible;
    }
  }

  .history-pagination {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    padding: 10px 0;
    flex-shrink: 0;
  }
}

.stats-container {
  .total-stats-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    
    :deep(.el-card__body) {
      padding: 30px;
    }
    
    .total-stats {
      display: flex;
      justify-content: center;
      align-items: center;
      
      .total-stat-item {
        text-align: center;
        color: white;
        
        .total-stat-value {
          font-size: 48px;
          font-weight: 700;
          margin-bottom: 10px;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .total-stat-label {
          font-size: 18px;
          opacity: 0.9;
        }
      }
    }
  }
  
  .card-header-title {
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
  }
  
  .stat-item {
    margin-bottom: 20px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .stat-item-content {
      display: flex;
      align-items: center;
      gap: 15px;

      .stat-label {
        width: 100px;
        font-size: 14px;
        color: #2c3e50;
        font-weight: 500;
        flex-shrink: 0;
      }

      .stat-count {
        width: 50px;
        text-align: right;
        font-size: 14px;
        color: #409eff;
        font-weight: 600;
        flex-shrink: 0;
      }
    }
  }
}

.json-path-tool {
  .path-input-panel {
    margin-bottom: 15px;
    
    h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      font-weight: 600;
      color: #2c3e50;
    }
  }
  
  .json-input-panel {
    h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      font-weight: 600;
      color: #2c3e50;
    }
  }
}

.json-format-tool {
  .json-input-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    min-width: 0;
    
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      padding: 10px;
      background: #f5f7fa;
      border-radius: 6px;
      
      h4 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: #2c3e50;
      }
      
      .input-stats,
      .output-stats {
        display: flex;
        gap: 15px;
        font-size: 12px;
        color: #606266;
        
        span {
          padding: 2px 8px;
          background: #fff;
          border-radius: 4px;
          border: 1px solid #dcdfe6;
        }
      }
    }
    
    .result-display {
      flex: 1;
      overflow: auto;
      overflow-x: auto;
      padding: 10px;
      background: #f5f7fa;
      border-radius: 6px;
      border: 1px solid #dcdfe6;
      display: flex;
      flex-direction: column;
      min-width: 0;
      
      pre {
        margin: 0;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.5;
        color: #2c3e50;
        white-space: pre;
        word-wrap: normal;
        min-width: fit-content;
        overflow-x: auto;
      }
    }
    
    .result-empty {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 200px;
      background: #f5f7fa;
      border-radius: 6px;
      border: 1px solid #dcdfe6;
    }
  }
  
  .json-tree-view {
    display: flex;
    flex-direction: column;
    min-width: 0;
    
    .json-tree-actions {
      display: flex;
      gap: 10px;
      margin-bottom: 10px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e9ecef;
    }
    
    .json-tree {
      flex: 1;
      overflow: auto;
      overflow-x: auto;
      background: #fff;
      border-radius: 4px;
      padding: 10px;
      max-height: 280px;
      min-width: fit-content;
      
      :deep(.el-tree-node) {
        min-width: fit-content;
      }
      
      :deep(.el-tree-node__content) {
        padding: 4px 0;
        height: auto;
        min-width: fit-content;
      }
      
      :deep(.el-tree-node__label) {
        font-family: 'Courier New', monospace;
        font-size: 13px;
        white-space: nowrap;
      }
    }
    
    .json-tree-node {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      
      .json-node-label {
        white-space: nowrap;
      }
      
      &.json-type-object {
        color: #e91e63;
      }
      
      &.json-type-array {
        color: #9c27b0;
      }
      
      &.json-type-string {
        color: #4caf50;
      }
      
      &.json-type-number {
        color: #2196f3;
      }
      
      &.json-type-boolean {
        color: #ff9800;
      }
      
      &.json-type-null {
        color: #9e9e9e;
      }
    }
  }
  
  .format-options {
    margin-top: 15px;
    padding: 15px;
    background: #f0f2f5;
    border-radius: 8px;
    
    .options-bar {
      display: flex;
      align-items: center;
      gap: 30px;
      flex-wrap: wrap;
      
      .option-group {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .option-label {
          font-size: 14px;
          color: #606266;
          font-weight: 500;
        }
      }
    }
  }
}

.json-diff-tool {
  .json-input-panel {
    margin-bottom: 15px;
    
    h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      font-weight: 600;
      color: #2c3e50;
    }
  }
  
  .diff-options {
    margin-top: 15px;
    padding: 15px;
    background: #f0f2f5;
    border-radius: 8px;
  }
}

.image-upload {
  width: 100%;
  
  :deep(.el-upload) {
    width: 100%;
  }
  
  :deep(.el-upload-dragger) {
    width: 100%;
    height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 2px dashed #d9d9d9;
    border-radius: 8px;
    background: #fafafa;
    transition: all 0.3s;
    
    &:hover {
      border-color: #409eff;
      background: #f0f9ff;
    }
  }
  
  .el-upload__tip {
    margin-top: 10px;
    color: #909399;
    font-size: 12px;
  }
}

.qr-code-upload {
  width: 100%;
  
  :deep(.el-upload) {
    width: 100%;
  }
  
  :deep(.el-upload-dragger) {
    width: 100%;
    height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 2px dashed #d9d9d9;
    border-radius: 8px;
    background: #fafafa;
    transition: all 0.3s;
    
    &:hover {
      border-color: #409eff;
      background: #f0f9ff;
    }
  }
  
  .upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    
    .upload-icon {
      font-size: 48px;
      color: #c0c4cc;
    }
    
    .upload-text {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
    }
    
    .upload-tip {
      font-size: 12px;
      color: #909399;
    }
  }
  
  .upload-preview {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    
    img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
    
    .upload-mask {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;
      color: #fff;
      opacity: 0;
      transition: opacity 0.3s;
      cursor: pointer;
      
      &:hover {
        opacity: 1;
      }
      
      .el-icon {
        font-size: 24px;
      }
      
      span {
        font-size: 14px;
      }
    }
  }
}

.image-preview {
  width: 100%;
  max-width: 400px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 10px;
  
  img {
    width: 100%;
    height: auto;
    display: block;
  }
}

.json-path-tool {
  .path-input-panel {
    margin-bottom: 15px;
    
    h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      font-weight: 600;
      color: #2c3e50;
    }
  }
  
  .json-input-panel {
    margin-bottom: 15px;
    
    h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      font-weight: 600;
      color: #2c3e50;
    }
  }
  
  .result-display {
    height: 100%;
    min-height: 300px;
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 15px;
    overflow: auto;
    overflow-x: auto;
    display: flex;
    flex-direction: column;
    min-width: 0;
    
    pre {
      margin: 0;
      padding: 10px;
      background: #fff;
      border-radius: 4px;
      max-height: 280px;
      font-size: 13px;
      line-height: 1.4;
      white-space: pre;
      word-wrap: normal;
      min-width: fit-content;
      overflow-x: auto;
    }
  }
  
  .result-empty {
    height: 100%;
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .json-tree-view {
    display: flex;
    flex-direction: column;
    min-width: 0;
    
    .json-tree-actions {
      display: flex;
      gap: 10px;
      margin-bottom: 10px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e9ecef;
    }
    
    .json-tree {
      flex: 1;
      overflow: auto;
      overflow-x: auto;
      background: #fff;
      border-radius: 4px;
      padding: 10px;
      max-height: 280px;
      min-width: fit-content;
      
      :deep(.el-tree-node) {
        min-width: fit-content;
      }
      
      :deep(.el-tree-node__content) {
        padding: 4px 0;
        height: auto;
        min-width: fit-content;
      }
      
      :deep(.el-tree-node__label) {
        font-family: 'Courier New', monospace;
        font-size: 13px;
        white-space: nowrap;
      }
    }
    
    .json-tree-node {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      
      .json-node-label {
        white-space: nowrap;
      }
      
      &.json-type-object {
        color: #e91e63;
      }
      
      &.json-type-array {
        color: #9c27b0;
      }
      
      &.json-type-string {
        color: #4caf50;
      }
      
      &.json-type-number {
        color: #2196f3;
      }
      
      &.json-type-boolean {
        color: #ff9800;
      }
      
      &.json-type-null {
        color: #9e9e9e;
      }
    }
  }
}
</style>
