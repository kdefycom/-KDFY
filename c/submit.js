// Configuração Supabase
const SUPABASE_URL = 'SUA_URL_SUPABASE_AQUI';
const SUPABASE_ANON_KEY = 'SUA_CHAVE_ANONIMA_AQUI';
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Elementos DOM
const submitForm = document.getElementById('submitForm');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');

// Validar link do WhatsApp
function isValidWhatsAppLink(url) {
    return url.includes('chat.whatsapp.com') || url.includes('wa.me');
}

// Mostrar mensagem
function showMessage(element, message, isError = false) {
    element.textContent = message;
    element.style.display = 'block';
    
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// Enviar formulário
submitForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Limpar mensagens
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    
    // Coletar dados
    const groupData = {
        name: document.getElementById('groupName').value.trim(),
        description: document.getElementById('groupDescription').value.trim(),
        whatsapp_link: document.getElementById('whatsappLink').value.trim(),
        category: document.getElementById('category').value,
        image_url: document.getElementById('imageUrl').value.trim() || null,
        status: 'pending'
    };
    
    // Validações
    if (!groupData.name || groupData.name.length < 3) {
        showMessage(errorMessage, 'O nome do grupo deve ter pelo menos 3 caracteres', true);
        return;
    }
    
    if (!groupData.description || groupData.description.length < 10) {
        showMessage(errorMessage, 'A descrição deve ter pelo menos 10 caracteres', true);
        return;
    }
    
    if (!isValidWhatsAppLink(groupData.whatsapp_link)) {
        showMessage(errorMessage, 'Link do WhatsApp inválido. Use um link de convite válido.', true);
        return;
    }
    
    if (!groupData.category) {
        showMessage(errorMessage, 'Selecione uma categoria', true);
        return;
    }
    
    try {
        // Desabilitar botão
        const submitBtn = submitForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';
        
        // Inserir no banco
        const { data, error } = await supabase
            .from('pending_groups')
            .insert([groupData])
            .select();
        
        if (error) throw error;
        
        // Sucesso
        showMessage(successMessage, 'Grupo enviado com sucesso! Aguarde a aprovação.', false);
        submitForm.reset();
        
        // Reabilitar botão
        submitBtn.disabled = false;
        submitBtn.textContent = 'Enviar para Aprovação';
        
        // Redirecionar após 3 segundos
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 3000);
        
    } catch (error) {
        console.error('Erro ao enviar grupo:', error);
        showMessage(errorMessage, 'Erro ao enviar grupo. Tente novamente.', true);
        
        // Reabilitar botão
        const submitBtn = submitForm.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Enviar para Aprovação';
    }
});
