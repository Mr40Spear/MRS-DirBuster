#!/bin/bash

# Python3-pip'in yüklü olup olmadığını kontrol et
if ! command -v pip3 &> /dev/null
then
    echo -e "\e[31m pip3 komutu bulunamadı, lütfen önce pip'i yükleyin.\e[0m"
    exit 1
fi

# Yükleniyor animasyonu
function loading_animation {
    spin='-\|/'
    i=0
    while kill -0 $1 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\r\e[34m$2 yükleniyor... ${spin:$i:1}\e[0m"
        sleep .1
    done
}

# Kütüphane yükleme fonksiyonu
function install_package {
    local package=$1
    echo -ne "\e[34m$package yükleniyor...\e[0m"
    pip3 install $package &> /dev/null &
    loading_animation $! $package
    wait $!
    if [ $? -eq 0 ]; then
        echo -e "\r\e[32m$package başarıyla yüklendi.\e[0m"
    else
        echo -e "\r\e[31m$package yüklenemedi.\e[0m"
    fi
}

# Gerekli Python kütüphanelerini yükle
echo -e "\e[34mKütüphaneler yükleniyor...\e[0m"

install_package "requests"
install_package "rich"
install_package "argparse"
install_package "aiohttp"


echo -e "\e[32mTüm kütüphaneler başarıyla yüklendi.\e[0m"
