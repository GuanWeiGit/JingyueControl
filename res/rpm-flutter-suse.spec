Name:       jingyue_control
Version:    1.4.6
Release:    0
Summary:    RPM package
License:    GPL-3.0
URL:        https://jingyue.rqrt2122.cn
Vendor:     JingyueControl <info@jingyue.rqrt2122.cn>
Requires:   gtk3 libxcb1 libXfixes3 alsa-utils libXtst6 libva2 pam gstreamer-plugins-base gstreamer-plugin-pipewire
Recommends: libayatana-appindicator3-1 xdotool
Provides:   libdesktop_drop_plugin.so()(64bit), libdesktop_multi_window_plugin.so()(64bit), libfile_selector_linux_plugin.so()(64bit), libflutter_custom_cursor_plugin.so()(64bit), libflutter_linux_gtk.so()(64bit), libscreen_retriever_plugin.so()(64bit), libtray_manager_plugin.so()(64bit), liburl_launcher_linux_plugin.so()(64bit), libwindow_manager_plugin.so()(64bit), libwindow_size_plugin.so()(64bit), libtexture_rgba_renderer_plugin.so()(64bit)

# https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/

%description
JingyueControl - Remote Desktop Software

%prep
# we have no source, so nothing here

%build
# we have no source, so nothing here

# %global __python %{__python3}

%install

mkdir -p "%{buildroot}/usr/share/jingyue_control" && cp -r ${HBB}/flutter/build/linux/x64/release/bundle/* -t "%{buildroot}/usr/share/jingyue_control"
mkdir -p "%{buildroot}/usr/bin"
install -Dm 644 $HBB/res/jingyue_control.service -t "%{buildroot}/usr/share/jingyue_control/files"
install -Dm 644 $HBB/res/jingyue_control.desktop -t "%{buildroot}/usr/share/jingyue_control/files"
install -Dm 644 $HBB/res/jingyue_control-link.desktop -t "%{buildroot}/usr/share/jingyue_control/files"
install -Dm 644 $HBB/res/128x128@2x.png "%{buildroot}/usr/share/icons/hicolor/256x256/apps/jingyue_control.png"
install -Dm 644 $HBB/res/scalable.svg "%{buildroot}/usr/share/icons/hicolor/scalable/apps/jingyue_control.svg"

%files
/usr/share/jingyue_control/*
/usr/share/jingyue_control/files/jingyue_control.service
/usr/share/icons/hicolor/256x256/apps/jingyue_control.png
/usr/share/icons/hicolor/scalable/apps/jingyue_control.svg
/usr/share/jingyue_control/files/jingyue_control.desktop
/usr/share/jingyue_control/files/jingyue_control-link.desktop

%changelog
# let's skip this for now

%pre
# can do something for centos7
case "$1" in
  1)
    # for install
  ;;
  2)
    # for upgrade
    systemctl stop jingyue_control || true
  ;;
esac

%post
cp /usr/share/jingyue_control/files/jingyue_control.service /etc/systemd/system/jingyue_control.service
cp /usr/share/jingyue_control/files/jingyue_control.desktop /usr/share/applications/
cp /usr/share/jingyue_control/files/jingyue_control-link.desktop /usr/share/applications/
ln -sf /usr/share/jingyue_control/jingyue_control /usr/bin/jingyue_control
systemctl daemon-reload
systemctl enable jingyue_control
systemctl start jingyue_control
update-desktop-database

%preun
case "$1" in
  0)
    # for uninstall
    systemctl stop jingyue_control || true
    systemctl disable jingyue_control || true
    rm /etc/systemd/system/jingyue_control.service || true
  ;;
  1)
    # for upgrade
  ;;
esac

%postun
case "$1" in
  0)
    # for uninstall
    rm /usr/bin/jingyue_control || true
    rmdir /usr/lib/jingyue_control || true
    rmdir /usr/local/jingyue_control || true
    rmdir /usr/share/jingyue_control || true
    rm /usr/share/applications/jingyue_control.desktop || true
    rm /usr/share/applications/jingyue_control-link.desktop || true
    update-desktop-database
  ;;
  1)
    # for upgrade
    rmdir /usr/lib/jingyue_control || true
    rmdir /usr/local/jingyue_control || true
  ;;
esac