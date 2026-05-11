Name:       jingyue_control
Version:    1.4.6
Release:    0
Summary:    RPM package for JingyueControl
License:    GPL-3.0
URL:        https://jingyue.rqrt2122.cn
Vendor:     JingyueControl <info@jingyue.rqrt2122.cn>
Requires:   gtk3 libxcb libXfixes alsa-lib libva2 pam gstreamer1-plugins-base
Recommends: libayatana-appindicator-gtk3 libxdo

# https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/

%description
JingyueControl (鲸跃远控) - The best open-source remote desktop client software, written in Rust.

%prep
# we have no source, so nothing here

%build
# we have no source, so nothing here

%global __python %{__python3}

%install
mkdir -p %{buildroot}/usr/bin/
mkdir -p %{buildroot}/usr/share/jingyue_control/
mkdir -p %{buildroot}/usr/share/jingyue_control/files/
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps/
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps/
install -m 755 $HBB/target/release/jingyue_control %{buildroot}/usr/bin/jingyue_control
install $HBB/libsciter-gtk.so %{buildroot}/usr/share/jingyue_control/libsciter-gtk.so
install $HBB/res/jingyue_control.service %{buildroot}/usr/share/jingyue_control/files/
install $HBB/res/128x128@2x.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/jingyue_control.png
install $HBB/res/scalable.svg %{buildroot}/usr/share/icons/hicolor/scalable/apps/jingyue_control.svg
install $HBB/res/jingyue_control.desktop %{buildroot}/usr/share/jingyue_control/files/
install $HBB/res/jingyue_control-link.desktop %{buildroot}/usr/share/jingyue_control/files/

%files
/usr/bin/jingyue_control
/usr/share/jingyue_control/libsciter-gtk.so
/usr/share/jingyue_control/files/jingyue_control.service
/usr/share/icons/hicolor/256x256/apps/jingyue_control.png
/usr/share/icons/hicolor/scalable/apps/jingyue_control.svg
/usr/share/jingyue_control/files/jingyue_control.desktop
/usr/share/jingyue_control/files/jingyue_control-link.desktop
/usr/share/jingyue_control/files/__pycache__/*

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
    rm /usr/share/applications/jingyue_control.desktop || true
    rm /usr/share/applications/jingyue_control-link.desktop || true
    update-desktop-database
  ;;
  1)
    # for upgrade
  ;;
esac