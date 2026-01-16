import elementEn from 'element-plus/es/locale/lang/en'
import common from './common.js'
import navModule from './nav.js'
import auth from './auth.js'
import projectModule from './project.js'
import testcaseModule from './testcase.js'
import execution from './execution.js'
import report from './report.js'
import reviewModule from './review.js'
import version from './version.js'
import requirementModule from './requirement.js'
import apiTestingModule from './api-testing.js'
import uiAutomationModule from './ui-automation.js'
import configurationModule from './configuration.js'
import assistantModule from './assistant.js'

export default {
  // 模块化导出
  common,
  auth,
  execution,
  report,
  version,

  // 导航模块
  nav: navModule.nav,
  modules: navModule.modules,
  menu: navModule.menu,

  // 项目模块
  project: projectModule.project,
  home: projectModule.home,
  profile: projectModule.profile,

  // 测试用例模块
  testcase: testcaseModule.testcase,
  testSuite: testcaseModule.testSuite,

  // 评审模块
  reviewList: reviewModule.reviewList,
  reviewTemplate: reviewModule.reviewTemplate,

  // 需求分析模块
  requirementAnalysis: requirementModule.requirementAnalysis,
  generatedTestCases: requirementModule.generatedTestCases,
  promptConfig: requirementModule.promptConfig,

  // API Testing Module
  apiTesting: apiTestingModule,

  // UI Automation Module
  uiAutomation: uiAutomationModule,

  // Configuration Center Module
  configuration: configurationModule,

  // AI Assistant Module
  assistant: assistantModule,

  // Element Plus 语言包
  ...elementEn
}
