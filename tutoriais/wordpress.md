# Instalação do WordPress na Segunda Instância.

## Instalar os pacotes necessários

```bash
apt-get install apache2 php-mysql php-curl libapache2-mod-php php-gd php-mbstring php-xml php-xmlrpc php-soap php-intl php-zip
```

## Configurar o Apache

```bash
cat<<EOF > /etc/apache2/sites-available/wordpress.conf
<Directory /var/www/html/wordpress/>
    AllowOverride All
</Directory>
EOF
a2enmod rewrite
a2ensite wordpress
```

## Baixar o WordPress

```bash
curl -O https://wordpress.org/latest.tar.gz
tar xzvf latest.tar.gz
touch wordpress/.htaccess
cp -a wordpress/. /var/www/html/wordpress
chown -R www-data:www-data /var/www/html/wordpress
find /var/www/html/wordpress/ -type d -exec chmod 750 {} \;
find /var/www/html/wordpress/ -type f -exec chmod 640 {} \;
systemctl restart apache2
```

## Criar arquivo de configuração

Aqui um exemplo de como você pode criar a configuração. Terá que substitiuir as variáveis com os valores que usou na criação do bano e das máquinas virtuais.

```bash
#!/bin/bash
BD=
USER=
PASSWORD=
HOST=

cat<<EOF > wp-config.php
<?php
define( 'DB_NAME', '$BD' );
define( 'DB_USER', '$USER' );
define( 'DB_PASSWORD', '$PASSWORD' );
define( 'DB_HOST', '$HOST' );
define( 'DB_CHARSET', 'utf8' );
define( 'DB_COLLATE', '' );

$(curl -s https://api.wordpress.org/secret-key/1.1/salt/)

\$table_prefix = 'wp_';

define( 'WP_DEBUG', false );

if ( ! defined( 'ABSPATH' ) ) {
        define( 'ABSPATH', __DIR__ . '/' );
}

require_once ABSPATH . 'wp-settings.php';
EOF
```

Depois seria mover o arquivo criado para a pasta de instalação do WordPress e reiniciar o Apache uma última vez:

```bash
cp wp-config.php /var/www/html/wordpress/
systemctl restart apache2
```

## Referências
[Ubuntu 20.04 Wordpress with Apache installation](https://linuxconfig.org/ubuntu-20-04-wordpress-with-apache-installation)

[Como instalar o WordPress com o LAMP no Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-wordpress-with-lamp-on-ubuntu-18-04-pt)
