PORTS = {
    # Acesso Remoto
    21:    {"service": "FTP",           "risk": "CRITICAL",  "context": "Protocolo sem criptografia. Credenciais trafegam em texto puro."},
    22:    {"service": "SSH",           "risk": "ATTENTION", "context": "Acesso remoto. Verifique se está restrito a IPs confiáveis."},
    23:    {"service": "Telnet",        "risk": "CRITICAL",  "context": "Protocolo obsoleto e inseguro. Nunca deve estar exposto."},
    3389:  {"service": "RDP",           "risk": "CRITICAL",  "context": "Alvo frequente de ataques de força bruta e ransomware."},
    5900:  {"service": "VNC",           "risk": "CRITICAL",  "context": "Acesso remoto de desktop. Frequentemente sem autenticação forte."},

    # Web
    80:    {"service": "HTTP",          "risk": "COMMON",    "context": "Tráfego não criptografado. Prefira HTTPS."},
    443:   {"service": "HTTPS",         "risk": "COMMON",    "context": "Verifique validade do certificado e headers de segurança."},
    8080:  {"service": "HTTP-Alt",      "risk": "ATTENTION", "context": "Porta alternativa HTTP. Frequentemente usada em dev sem segurança."},
    8443:  {"service": "HTTPS-Alt",     "risk": "ATTENTION", "context": "Porta alternativa HTTPS. Verifique configuração."},
    8888:  {"service": "HTTP-Dev",      "risk": "ATTENTION", "context": "Porta comum de Jupyter Notebook. Pode expor código e dados."},
    3000:  {"service": "Node/React",    "risk": "ATTENTION", "context": "Servidor de desenvolvimento. Não deve estar exposto em produção."},
    5000:  {"service": "Flask/Dev",     "risk": "ATTENTION", "context": "Servidor Flask em modo dev. Expõe debugger e dados sensíveis."},
    5173:  {"service": "Vite/Dev",      "risk": "ATTENTION", "context": "Servidor Vite de desenvolvimento. Não deve estar em produção."},
    4200:  {"service": "Angular/Dev",   "risk": "ATTENTION", "context": "Servidor Angular dev. Não deve estar exposto."},

    # Bancos de Dados
    3306:  {"service": "MySQL",         "risk": "CRITICAL",  "context": "Banco de dados exposto. Nunca deve ser acessível externamente."},
    5432:  {"service": "PostgreSQL",    "risk": "CRITICAL",  "context": "Banco de dados exposto. Restrinja acesso por firewall."},
    1433:  {"service": "MSSQL",         "risk": "CRITICAL",  "context": "SQL Server exposto. Alto risco de vazamento de dados."},
    1521:  {"service": "Oracle DB",     "risk": "CRITICAL",  "context": "Banco Oracle exposto. Restrinja acesso imediatamente."},
    27017: {"service": "MongoDB",       "risk": "CRITICAL",  "context": "MongoDB frequentemente configurado sem autenticação por padrão."},
    6379:  {"service": "Redis",         "risk": "CRITICAL",  "context": "Redis geralmente sem senha por padrão. Risco crítico de exposição."},
    9200:  {"service": "Elasticsearch", "risk": "CRITICAL",  "context": "Elasticsearch sem autenticação por padrão. Expõe todos os dados."},
    5984:  {"service": "CouchDB",       "risk": "CRITICAL",  "context": "CouchDB pode estar sem autenticação. Verifique configuração."},
    6380:  {"service": "Redis-Alt",     "risk": "CRITICAL",  "context": "Porta alternativa Redis. Mesmo risco da porta padrão."},

    # Mensageria e Cache
    5672:  {"service": "RabbitMQ",      "risk": "ATTENTION", "context": "Message broker. Verifique autenticação e permissões."},
    15672: {"service": "RabbitMQ-UI",   "risk": "CRITICAL",  "context": "Interface web do RabbitMQ. Nunca deve estar exposta publicamente."},
    9092:  {"service": "Kafka",         "risk": "ATTENTION", "context": "Message broker Kafka. Verifique autenticação."},
    11211: {"service": "Memcached",     "risk": "CRITICAL",  "context": "Memcached sem autenticação por padrão. Risco de exposição de dados."},

    # Infraestrutura e DevOps
    2375:  {"service": "Docker API",    "risk": "CRITICAL",  "context": "API Docker sem TLS. Permite controle total do servidor."},
    2376:  {"service": "Docker TLS",    "risk": "ATTENTION", "context": "API Docker com TLS. Verifique certificados."},
    2379:  {"service": "etcd",          "risk": "CRITICAL",  "context": "Banco de dados do Kubernetes. Contém secrets e configurações."},
    6443:  {"service": "K8s API",       "risk": "CRITICAL",  "context": "API do Kubernetes exposta. Risco crítico."},
    10250: {"service": "Kubelet",       "risk": "CRITICAL",  "context": "Kubelet exposto. Permite execução de comandos nos pods."},
    9000:  {"service": "Portainer/SonarQube", "risk": "ATTENTION", "context": "Interface de gestão. Verifique autenticação."},

    # Rede e DNS
    53:    {"service": "DNS",           "risk": "ATTENTION", "context": "Servidor DNS exposto. Verifique se é intencional."},
    25:    {"service": "SMTP",          "risk": "ATTENTION", "context": "Servidor de email. Pode ser usado para spam se mal configurado."},
    110:   {"service": "POP3",          "risk": "ATTENTION", "context": "Email sem criptografia. Prefira POP3S."},
    143:   {"service": "IMAP",          "risk": "ATTENTION", "context": "Email sem criptografia. Prefira IMAPS."},
    135:   {"service": "RPC",           "risk": "CRITICAL",  "context": "RPC Windows exposto. Vetor comum de exploração."},
    139:   {"service": "NetBIOS",       "risk": "CRITICAL",  "context": "NetBIOS exposto. Permite enumeração de usuários e shares."},
    445:   {"service": "SMB",           "risk": "CRITICAL",  "context": "SMB exposto. Vetor do WannaCry e outros ransomwares."},

    # Monitoramento
    9090:  {"service": "Prometheus",    "risk": "ATTENTION", "context": "Métricas expostas. Pode revelar informações da infraestrutura."},
    3100:  {"service": "Loki",          "risk": "ATTENTION", "context": "Logs expostos. Pode conter informações sensíveis."},
    # 9090 is duplicated in the prompt, I'll keep the first one or combine if necessary, but prompt says:
    # 9090:  {"service": "Prometheus",    "risk": "ATTENTION", "context": "Métricas expostas. Pode revelar informações da infraestrutura."},
    # 9090:  {"service": "Grafana-Alt",   "risk": "ATTENTION", "context": "Interface de monitoramento. Verifique autenticação."},
    # In Python, the last one wins. I'll stick to the prompt's provided list.
    3001:  {"service": "Grafana",       "risk": "ATTENTION", "context": "Dashboard Grafana. Verifique se está protegido por senha."},
}

HTTP_CHECKS = [
    {"path": "/admin",           "label": "Painel Admin",        "risk": "CRITICAL"},
    {"path": "/administrator",   "label": "Painel Admin",        "risk": "CRITICAL"},
    {"path": "/.env",            "label": "Arquivo .env exposto","risk": "CRITICAL"},
    {"path": "/.env.local",      "label": "Arquivo .env exposto","risk": "CRITICAL"},
    {"path": "/api/docs",        "label": "API Docs exposta",    "risk": "ATTENTION"},
    {"path": "/docs",            "label": "Documentação exposta","risk": "ATTENTION"},
    {"path": "/swagger",         "label": "Swagger exposto",     "risk": "ATTENTION"},
    {"path": "/swagger-ui.html", "label": "Swagger exposto",     "risk": "ATTENTION"},
    {"path": "/graphql",         "label": "GraphQL exposto",     "risk": "ATTENTION"},
    {"path": "/api/v1",          "label": "API endpoint exposto","risk": "ATTENTION"},
    {"path": "/api/v2",          "label": "API endpoint exposto","risk": "ATTENTION"},
    {"path": "/phpinfo.php",     "label": "PHPInfo exposto",     "risk": "CRITICAL"},
    {"path": "/wp-admin",        "label": "WordPress Admin",     "risk": "CRITICAL"},
    {"path": "/wp-login.php",    "label": "WordPress Login",     "risk": "ATTENTION"},
    {"path": "/.git",            "label": "Git exposto",         "risk": "CRITICAL"},
    {"path": "/backup",          "label": "Backup exposto",      "risk": "CRITICAL"},
    {"path": "/config",          "label": "Config exposta",      "risk": "CRITICAL"},
    {"path": "/server-status",   "label": "Apache Status",       "risk": "ATTENTION"},
    {"path": "/actuator",        "label": "Spring Actuator",     "risk": "CRITICAL"},
    {"path": "/actuator/env",    "label": "Spring Env exposto",  "risk": "CRITICAL"},
]

HTTP_SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
]
