// Configuração Supabase
const SUPABASE_URL = 'SUA_URL_SUPABASE_AQUI';
const SUPABASE_ANON_KEY = 'SUA_CHAVE_ANONIMA_AQUI';
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Senha admin (em produção, use autenticação adequada)
const ADMIN_PASSWORD = 'admin123';

// Elementos DOM
const loginSection = document.getElementById('loginSection');
const adminContent = document.getElementById('adminContent');
const loginForm = document.getElementById('loginForm');
const loadingState = document.getElementById('loadingState');
const pendingGroups = document.getElementById('pendingGroups');
const emptyState = document.getElementById('emptyState');

// Verificar se já está logado
if (localStorage.getItem('adminLogged') === 'true') {
    showAdminPanel();
}

// Login
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const password = document.getElementById('adminPassword').value;
    
    if (password === ADMIN_PASSWORD) {
        localStorage.setItem('adminLogged', 'true');
        showAdminPanel();
    } else {
        alert('Senha incorreta!');
    }
});

// Mostrar painel admin
function showAdminPanel() {
    loginSection.style.display = 'none';
    adminContent.style.display = 'block';
    loadPendingGroups();
}

// Carregar grupos pendentes
async function loadPendingGroups() {
    try {
        loadingState.style.display = 'block';
        pendingGroups.innerHTML = '';
        emptyState.style.display = 'none';
        
        const { data, error } = await supabase
            .from('pending_groups')
            .select('*')
            .eq('status', 'pending')
            .order('created_at', { ascending: false });
        
        if (error) throw error;
        
        if (!data || data.length === 0) {
            emptyState.style.display = 'block';
            return;
        }
        
        pendingGroups.innerHTML = data.map(group => createAdminCard(group)).join('');
        
        // Adicionar event listeners
        document.querySelectorAll('.approve-btn').forEach(btn => {
            btn.addEventListener('click', () => approveGroup(btn.dataset.id));
        });
        
        document.querySelectorAll('.reject-btn').forEach(btn => {
            btn.addEventListener('click', () => rejectGroup(btn.dataset.id));
        });
        
    } catch (error) {
        console.error('Erro ao carregar grupos pendentes:', error);
        alert('Erro ao carregar grupos pendentes');
    } finally {
        loadingState.style.display = 'none';
    }
}

// Criar card admin
function createAdminCard(group) {
    const defaultImage = 'https://via.placeholder.com/400x300/8b5cf6/ffffff?text=Grupo+WhatsApp';
    const imageUrl = group.image_url || defaultImage;
    
    return `
        <div class="admin-card">
            <img src="${imageUrl}" alt="${group.name}" class="admin-card-image"
                 onerror="this.src='${defaultImage}'">
            <div class="admin-card-content">
                <h3>${group.name}</h3>
                <p><strong>Categoria:</strong> ${group.category || 'Não especificada'}</p>
                <p><strong>Descrição:</strong> ${group.description}</p>
                <p><strong>Link:</strong> <a href="${group.whatsapp_link}" target="_blank" 
                   style="color: var(--primary);">Ver link</a></p>
                <p><strong>Enviado em:</strong> ${new Date(group.created_at).toLocaleDateString('pt-BR')}</p>
            </div>
            <div class="admin-card-actions">
                <button class="btn btn-success approve-btn" data-id="${group.id}">
                    ✓ Aprovar
                </button>
                <button class="btn btn-danger reject-btn" data-id="${group.id}">
                    ✗ Rejeitar
                </button>
            </div>
        </div>
    `;
}

// Aprovar grupo
async function approveGroup(groupId) {
    if (!confirm('Tem certeza que deseja aprovar este grupo?')) return;
    
    try {
        // Buscar dados do grupo pendente
        const { data: pendingGroup, error: fetchError } = await supabase
            .from('pending_groups')
            .select('*')
            .eq('id', groupId)
            .single();
        
        if (fetchError) throw fetchError;
        
        // Inserir em grupos aprovados
        const { error: insertError } = await supabase
            .from('approved_groups')
            .insert([{
                name: pendingGroup.name,
                description: pendingGroup.description,
                whatsapp_link: pendingGroup.whatsapp_link,
                category: pendingGroup.category,
                image_url: pendingGroup.image_url,
                status: 'approved',
                created_at: pendingGroup.created_at
            }]);
        
        if (insertError) throw insertError;
        
        // Deletar de grupos pendentes
        const { error: deleteError } = await supabase
            .from('pending_groups')
            .delete()
            .eq('id', groupId);
        
        if (deleteError) throw deleteError;
        
        alert('Grupo aprovado com sucesso!');
        loadPendingGroups();
        
    } catch (error) {
        console.error('Erro ao aprovar grupo:', error);
        alert('Erro ao aprovar grupo. Tente novamente.');
    }
}

// Rejeitar grupo
async function rejectGroup(groupId) {
    if (!confirm('Tem certeza que deseja rejeitar este grupo?')) return;
    
    try {
        const { error } = await supabase
            .from('pending_groups')
            .delete()
            .eq('id', groupId);
        
        if (error) throw error;
        
        alert('Grupo rejeitado!');
        loadPendingGroups();
        
    } catch (error) {
        console.error('Erro ao rejeitar grupo:', error);
        alert('Erro ao rejeitar grupo. Tente novamente.');
    }
}
