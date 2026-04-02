export default function WordInput({ words, onChange, single = false }) {
  const value = words.join(', ')

  const handleChange = (e) => {
    const raw = e.target.value
    if (single) {
      onChange([raw.trim()])
    } else {
      onChange(raw.split(',').map(w => w.trim()).filter(Boolean))
    }
  }

  return (
    <div>
      <label className="text-xs text-gray-500 mb-1 block">
        {single ? '输入一个英文词汇' : '输入英文词汇（逗号分隔）'}
      </label>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={single ? '例如 reason' : '例如 reason, god, nature, law'}
        className="input w-full"
      />
    </div>
  )
}
