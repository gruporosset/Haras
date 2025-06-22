export function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  
  try {
    let date
    
    // Se já é formato ISO (YYYY-MM-DD ou YYYY-MM-DD HH:mm:ss)
    if (dateStr.includes('-')) {
      date = new Date(dateStr)
    } 
    // Se é formato brasileiro (DD/MM/YYYY ou DD/MM/YYYY HH:mm:ss)
    else if (dateStr.includes('/')) {
      const [datePart, timePart] = dateStr.split(' ')
      const [day, month, year] = datePart.split('/')
      const isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
      
      if (timePart) {
        date = new Date(`${isoDate}T${timePart}`)
      } else {
        // Se não houver parte de tempo, assume meia-noite
        // Isso é necessário para evitar problemas de fuso horário  
        const timePart2 = '00:00:00'
        date = new Date(`${isoDate}T${timePart2}`)
      }
    } else {
      date = new Date(dateStr)
    }
    
    if (isNaN(date.getTime())) {
      return dateStr // Retorna original se não conseguir converter
    }
    
    return date.toLocaleDateString('pt-BR')
  } catch {
    return dateStr
  }
}

export function formatDateTime(dateStr) {
  if (!dateStr) return 'N/A'
  
  try {
    let date
    
    if (dateStr.includes('-')) {
      date = new Date(dateStr)
    } else if (dateStr.includes('/')) {
      const [datePart, timePart] = dateStr.split(' ')
      const [day, month, year] = datePart.split('/')
      const isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
      date = new Date(`${isoDate}T${timePart || '00:00:00'}`)
    } else {
      date = new Date(dateStr)
    }
    
    if (isNaN(date.getTime())) {
      return dateStr
    }
    
    return date.toLocaleString('pt-BR')
  } catch {
    return dateStr
  }
}

export function formatDateForInput(dateStr) {
  if (!dateStr) return ''
  
  try {
    let date
    
    if (dateStr.includes('-')) {
      date = new Date(dateStr)
    } else if (dateStr.includes('/')) {
      const [datePart, timePart] = dateStr.split(' ')
      const [day, month, year] = datePart.split('/')
      const isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
      date = new Date(`${isoDate}T${timePart || '00:00:00'}`)
    } else {
      date = new Date(dateStr)
    }
    
    if (isNaN(date.getTime())) {
      return ''
    }
    
    return date.toISOString().slice(0, 16)
  } catch {
    return ''
  }
}

// ... funções existentes ...

export function convertToISO(dateStr) {
  if (!dateStr) return null
  
  try {
    // Se já está em formato ISO, retornar como está
    if (dateStr.includes('-') && !dateStr.includes('/')) {
      return dateStr
    }
    
    // Se é formato brasileiro (DD/MM/YYYY ou DD/MM/YYYY HH:mm:ss)
    if (dateStr.includes('/')) {
      const [datePart, timePart] = dateStr.split(' ')
      const [day, month, year] = datePart.split('/')
      let isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
      
      if (timePart) {
        isoDate += `T${timePart}`
        // Adicionar segundos se não existir
        if (timePart.split(':').length === 2) {
          isoDate += ':00'
        }
      } else {
        isoDate += 'T00:00:00'
      }
      
      return isoDate
    }
    
    return dateStr
  } catch {
    return dateStr
  }
}

export function prepareFormData(formData, dateFields = []) {
  const prepared = { ...formData }
  
  // Converter campos de data
  dateFields.forEach(field => {
    if (prepared[field]) {
      prepared[field] = convertToISO(prepared[field])
    }
  })
  
  // Converter objetos select para valores
  Object.keys(prepared).forEach(key => {
    if (typeof prepared[key] === 'object' && prepared[key]?.value !== undefined) {
      prepared[key] = prepared[key].value
    }
    
    // Converter strings vazias para null
    if (prepared[key] === '') {
      prepared[key] = null
    }
  })
  
  return prepared
}