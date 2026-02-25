import React from 'react';
import clsx from 'clsx';
import {useNavbarSecondaryMenu} from '@docusaurus/theme-common/internal';
import ReadingSettings from '@site/src/components/ReadingSettings';

export default function NavbarMobileSidebarLayout({header, primaryMenu, secondaryMenu}) {
  const {shown: secondaryMenuShown} = useNavbarSecondaryMenu();

  return (
    <div className="navbar-sidebar">
      {header}
      <div
        className={clsx('navbar-sidebar__items', {
          'navbar-sidebar__items--show-secondary': secondaryMenuShown,
        })}>
        <div className="navbar-sidebar__item menu">
          <ReadingSettings variant="panel" />
          {primaryMenu}
        </div>
        <div className="navbar-sidebar__item menu">{secondaryMenu}</div>
      </div>
    </div>
  );
}
