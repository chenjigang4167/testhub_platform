export const numberFormats = /** @type {const} */ ({
  'zh-cn': {
    currency: {
      style: 'currency',
      currency: 'CNY',
      currencyDisplay: 'symbol'
    },
    decimal: {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    },
    percent: {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    },
    integer: {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }
  },
  'en': {
    currency: {
      style: 'currency',
      currency: 'USD',
      currencyDisplay: 'symbol'
    },
    decimal: {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    },
    percent: {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    },
    integer: {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }
  }
})
