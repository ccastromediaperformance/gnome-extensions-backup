# gnome-extensions-backup
Ferramenta de Backup de Extensões do GNOME
Esta ferramenta foi criada para facilitar o backup das extensões instaladas no ambiente GNOME, garantindo que você possa salvar, restaurar e gerenciar suas extensões com facilidade. Desenvolvida em Python, ela é compatível com distribuições Linux que utilizam GNOME, com foco especial em sistemas Fedora, mas adaptável a outras.

### Funcionalidades Principais
- Lista e identifica as extensões GNOME atualmente instaladas no sistema.
- Realiza backup dos arquivos das extensões para um local seguro.
- Facilita a restauração das extensões a partir do backup, preservando configurações.
- Permite automação do processo para backups regulares, útil para usuários avançados.
- Compatível com ambientes que utilizam Flatpak e GTK, garantindo integração e portabilidade.

### Por que usar esta ferramenta?
As extensões do GNOME personalizam e aumentam a produtividade do seu ambiente de trabalho, mas podem ser perdidas em atualizações ou reinstalações do sistema. Esta ferramenta assegura que suas personalizações sejam facilmente recuperadas, evitando retrabalho.

### Como usar
1) Execute o script Python para realizar o backup das extensões instaladas.
2) O backup será salvo em um diretório especificado para fácil acesso.
3) Para restaurar, execute o script com o parâmetro de restauração, apontando para o backup desejado.
4) Pode ser integrada em scripts ou cron jobs para backups automáticos.

Requisitos
- Python 3.x
- Acesso ao diretório das extensões do GNOME (~/.local/share/gnome-shell/extensions/ ou /usr/share/gnome-shell/extensions/)
- Dependências específicas listadas no arquivo requirements.txt (se houver)

Desenvolvimento e Contribuição
Este projeto utiliza Flatpak/flatpak-builder no Fedora, facilitando a construção e distribuição da ferramenta. Contribuições são bem-vindas para melhorias e adaptações para outras distribuições.
