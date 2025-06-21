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