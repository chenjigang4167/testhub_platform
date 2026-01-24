export const pluralRules = {
  // 中文不区分单复数，始终返回第一个选项
  'zh-cn': (choice) => 0,

  // 英文标准复数规则
  // choice = 0 -> 第一个选项 (zero/none)
  // choice = 1 -> 第二个选项 (singular)
  // choice > 1 -> 第三个选项 (plural)
  'en': (choice, choicesLength) => {
    if (choice === 0) return 0
    if (choice === 1) return 1
    return 2
  }
}
