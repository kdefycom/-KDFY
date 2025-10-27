// Configuração Supabase
const SUPABASE_URL = 'SUA_URL_SUPABASE_AQUI';
const SUPABASE_ANON_KEY = 'SUA_CHAVE_ANONIMA_AQUI';
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Variáveis de estado
let currentPage = 1;
const itemsPerPage = 9;
let allGroups = [];
let filteredGroups = [];

// Elementos DOM
const groupsGrid = document.getElementById('groupsGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const categoryFilter = document.getElementById('categoryFilter');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const pageInfo = document.getElementById('pageInfo');

// Carregar grupos aprovados
async function loadGroups() {
    try {
        loadingState.style.display = 'block';
        groupsGrid.innerHTML = '';
        emptyState.style.display = 'none';

        const { data, error } = await supabase
            .from('approved_groups')
            .select('*')
            .order('approved_at', { ascending: false });

        if (error) throw error;

        allGroups = data || [];
        filteredGroups = allGroups;
        renderGroups();

    } catch (error) {
        console.error('Erro ao carregar grupos:', error);
        alert('Erro ao carregar grupos. Verifique a conexão com o banco de dados.');
    } finally {
        loadingState.style.display = 'none';
    }
}

// Renderizar grupos
function renderGroups() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const groupsToShow = filteredGroups.slice(startIndex, endIndex);

    if (groupsToShow.length === 0) {
        emptyState.style.display = 'block';
        groupsGrid.innerHTML = '';
        return;
    }

    emptyState.style.display = 'none';
    groupsGrid.innerHTML = groupsToShow.map(group => createGroupCard(group)).join('');

    // Atualizar paginação
    pageInfo.textContent = `Página ${currentPage}`;
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = endIndex >= filteredGroups.length;
}

// Criar card de grupo
function createGroupCard(group) {
    const defaultImage = 'https://via.placeholder.com/400x300/8b5cf6/ffffff?text=Grupo+WhatsApp';
    const imageUrl = group.image_url || defaultImage;

    return `
        <div class="group-card">
            <img src="${imageUrl}" alt="${group.name}" class="group-image" 
                 onerror="this.src='${defaultImage}'">
            <div class="group-content">
                <span class="group-category">${group.category || 'Outros'}</span>
                <h3 class="group-name">${group.name}</h3>
                <p class="group-description">${group.description}</p>
                <a href="${group.whatsapp_link}" target="_blank" rel="noopener noreferrer" 
                   class="btn btn-primary group-link">
                    Entrar no Grupo
                </a>
            </div>
        </div>
    `;
}

// Filtrar por categoria
function filterByCategory() {
    const selectedCategory = categoryFilter.value;
    
    if (selectedCategory === '') {
        filteredGroups = allGroups;
    } else {
        filteredGroups = allGroups.filter(group => group.category === selectedCategory);
    }
    
    currentPage = 1;
    renderGroups();
}

// Event Listeners
categoryFilter.addEventListener('change', filterByCategory);

prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        renderGroups();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

nextPageBtn.addEventListener('click', () => {
    const maxPages = Math.ceil(filteredGroups.length / itemsPerPage);
    if (currentPage < maxPages) {
        currentPage++;
        renderGroups();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

// Inicializar
loadGroups();
