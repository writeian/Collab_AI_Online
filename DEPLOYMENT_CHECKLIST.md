# 🚀 Digital Ocean Deployment Checklist

## **Pre-Deployment Preparation**

### **✅ Code Preparation**
- [ ] Fix SQLAlchemy relationship warning in `models.py`
- [ ] Update database paths for Linux (remove Windows paths)
- [ ] Update Gunicorn configuration for external access
- [ ] Test with `requirements_production.txt`
- [ ] Commit all changes to GitHub
- [ ] Create deployment branch if needed

### **✅ Environment Variables**
- [ ] Prepare production `.env` file with:
  - [ ] `SECRET_KEY` (strong random key)
  - [ ] `DATABASE_URL` (PostgreSQL connection string)
  - [ ] `ANTHROPIC_API_KEY`
  - [ ] `OPENAI_API_KEY`
  - [ ] `FLASK_ENV=production`
  - [ ] `GOOGLE_SERVICE_ACCOUNT_FILE` (if using Google Docs)

---

## **🖥️ Server Setup (Digital Ocean)**

### **✅ Initial Server Configuration**
- [ ] Create Digital Ocean droplet (Ubuntu 22.04 LTS recommended)
- [ ] Set up SSH key authentication
- [ ] Update system packages: `sudo apt update && sudo apt upgrade -y`
- [ ] Create non-root user with sudo privileges
- [ ] Configure firewall (UFW):
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 80
  sudo ufw allow 443
  sudo ufw enable
  ```

### **✅ Python Environment**
- [ ] Install Python 3.11+ and development tools:
  ```bash
  sudo apt install python3.11 python3.11-venv python3.11-dev
  sudo apt install python3-pip build-essential
  ```
- [ ] Create application directory:
  ```bash
  sudo mkdir -p /var/www/ai_collab_online
  sudo chown $USER:$USER /var/www/ai_collab_online
  ```

### **✅ Database Setup (PostgreSQL)**
- [ ] Install PostgreSQL:
  ```bash
  sudo apt install postgresql postgresql-contrib libpq-dev
  ```
- [ ] Create database and user:
  ```bash
  sudo -u postgres psql
  CREATE DATABASE ai_collab_online;
  CREATE USER ai_collab_user WITH PASSWORD 'your_secure_password';
  GRANT ALL PRIVILEGES ON DATABASE ai_collab_online TO ai_collab_user;
  \q
  ```
- [ ] Test database connection

### **✅ Web Server Setup (Nginx)**
- [ ] Install Nginx:
  ```bash
  sudo apt install nginx
  ```
- [ ] Configure Nginx as reverse proxy (see Nginx config below)
- [ ] Set up SSL certificate with Let's Encrypt:
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d yourdomain.com
  ```

---

## **📦 Application Deployment**

### **✅ Code Deployment**
- [ ] Clone repository to server:
  ```bash
  cd /var/www/ai_collab_online
  git clone https://github.com/writeian/Collab_AI_Online.git .
  ```
- [ ] Create virtual environment:
  ```bash
  python3.11 -m venv venv
  source venv/bin/activate
  ```
- [ ] Install dependencies:
  ```bash
  pip install -r requirements_production.txt
  ```

### **✅ Configuration Setup**
- [ ] Create production `.env` file:
  ```bash
  cp .env.example .env
  nano .env
  ```
- [ ] Set environment variables:
  ```env
  SECRET_KEY=your-super-secret-key-here
  DATABASE_URL=postgresql://ai_collab_user:password@localhost/ai_collab_online
  ANTHROPIC_API_KEY=your-anthropic-key
  OPENAI_API_KEY=your-openai-key
  FLASK_ENV=production
  ```
- [ ] Create necessary directories:
  ```bash
  mkdir -p instance logs static/uploads
  chmod 755 instance logs static/uploads
  ```

### **✅ Database Migration**
- [ ] Run Alembic migrations:
  ```bash
  alembic upgrade head
  ```
- [ ] Verify database tables created
- [ ] Test database connection from application

### **✅ WSGI Server Setup**
- [ ] Update Gunicorn configuration:
  ```python
  # deployment/gunicorn.conf.py
  bind = "127.0.0.1:8000"  # Keep local for Nginx proxy
  accesslog = "logs/access.log"
  errorlog = "logs/error.log"
  ```
- [ ] Test Gunicorn manually:
  ```bash
  gunicorn -c deployment/gunicorn.conf.py wsgi:app
  ```

---

## **🔧 Process Management**

### **✅ Systemd Service Setup**
- [ ] Create systemd service file:
  ```bash
  sudo nano /etc/systemd/system/ai_collab_online.service
  ```
- [ ] Service file content:
  ```ini
  [Unit]
  Description=AI Collab Online
  After=network.target

  [Service]
  User=www-data
  Group=www-data
  WorkingDirectory=/var/www/ai_collab_online
  Environment="PATH=/var/www/ai_collab_online/venv/bin"
  ExecStart=/var/www/ai_collab_online/venv/bin/gunicorn -c deployment/gunicorn.conf.py wsgi:app
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```
- [ ] Enable and start service:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable ai_collab_online
  sudo systemctl start ai_collab_online
  sudo systemctl status ai_collab_online
  ```

### **✅ Nginx Configuration**
- [ ] Create Nginx site configuration:
  ```bash
  sudo nano /etc/nginx/sites-available/ai_collab_online
  ```
- [ ] Configuration content:
  ```nginx
  server {
      listen 80;
      server_name yourdomain.com www.yourdomain.com;
      
      location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
      
      location /static/ {
          alias /var/www/ai_collab_online/static/;
          expires 1y;
          add_header Cache-Control "public, immutable";
      }
  }
  ```
- [ ] Enable site:
  ```bash
  sudo ln -s /etc/nginx/sites-available/ai_collab_online /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx
  ```

---

## **🧪 Testing & Verification**

### **✅ Application Testing**
- [ ] Test basic application access: `http://yourdomain.com`
- [ ] Test static files loading
- [ ] Test database connectivity
- [ ] Test AI API integration
- [ ] Test user registration/login
- [ ] Test chat functionality
- [ ] Test mobile responsiveness

### **✅ Performance Testing**
- [ ] Check application response times
- [ ] Monitor memory usage
- [ ] Test concurrent user access
- [ ] Verify log rotation working
- [ ] Check SSL certificate validity

### **✅ Security Verification**
- [ ] Verify HTTPS redirect working
- [ ] Check file permissions (no world-readable sensitive files)
- [ ] Test firewall rules
- [ ] Verify environment variables not exposed
- [ ] Check for any error messages in logs

---

## **📊 Monitoring & Maintenance**

### **✅ Log Monitoring**
- [ ] Set up log monitoring:
  ```bash
  sudo journalctl -u ai_collab_online -f
  tail -f /var/www/ai_collab_online/logs/error.log
  ```
- [ ] Configure log rotation:
  ```bash
  sudo nano /etc/logrotate.d/ai_collab_online
  ```

### **✅ Backup Strategy**
- [ ] Set up database backups:
  ```bash
  # Add to crontab
  0 2 * * * pg_dump ai_collab_online > /backups/db_$(date +\%Y\%m\%d).sql
  ```
- [ ] Set up application backups
- [ ] Test backup restoration

### **✅ Update Process**
- [ ] Document update procedure
- [ ] Set up staging environment (optional)
- [ ] Create rollback plan

---

## **🚨 Troubleshooting Common Issues**

### **❌ Application Won't Start**
- [ ] Check systemd service status: `sudo systemctl status ai_collab_online`
- [ ] Check logs: `sudo journalctl -u ai_collab_online -n 50`
- [ ] Verify environment variables
- [ ] Check file permissions

### **❌ Database Connection Issues**
- [ ] Verify PostgreSQL is running: `sudo systemctl status postgresql`
- [ ] Check database credentials
- [ ] Test connection manually: `psql -h localhost -U ai_collab_user -d ai_collab_online`

### **❌ Static Files Not Loading**
- [ ] Check Nginx configuration: `sudo nginx -t`
- [ ] Verify file permissions
- [ ] Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### **❌ SSL Certificate Issues**
- [ ] Check certificate validity: `sudo certbot certificates`
- [ ] Renew if needed: `sudo certbot renew`
- [ ] Verify Nginx SSL configuration

---

## **📋 Post-Deployment Checklist**

### **✅ Final Verification**
- [ ] All tests passing
- [ ] Application accessible via HTTPS
- [ ] Database migrations complete
- [ ] Static files loading correctly
- [ ] AI services working
- [ ] User registration/login functional
- [ ] Mobile interface working
- [ ] Logs being written correctly
- [ ] Monitoring alerts configured

### **✅ Documentation**
- [ ] Update deployment documentation
- [ ] Document server access procedures
- [ ] Create maintenance schedule
- [ ] Document backup/restore procedures
- [ ] Create incident response plan

### **✅ Security Review**
- [ ] Run security scan
- [ ] Verify no sensitive data exposed
- [ ] Check for open ports
- [ ] Review file permissions
- [ ] Test backup restoration

---

## **🎯 Success Criteria**

**Deployment is successful when:**
- ✅ Application accessible at `https://yourdomain.com`
- ✅ All core features working (chat, AI, user management)
- ✅ Database migrations complete without errors
- ✅ SSL certificate valid and working
- ✅ Static files loading correctly
- ✅ Mobile interface responsive
- ✅ Logs being written and rotated
- ✅ Monitoring and alerts configured
- ✅ Backup system functional

---

**📞 Emergency Contacts:**
- **Server Access**: SSH key + backup password
- **Database**: PostgreSQL admin credentials
- **Domain**: DNS provider access
- **SSL**: Let's Encrypt renewal process

**🔄 Rollback Plan:**
1. Stop application: `sudo systemctl stop ai_collab_online`
2. Restore from backup
3. Restart application: `sudo systemctl start ai_collab_online`
4. Verify functionality 