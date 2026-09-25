import React from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import {useThemeConfig} from '@docusaurus/theme-common';
import ThemedImage from '@theme/ThemedImage';

// Swizzled so the CoSTAR logo links to the CoSTAR website (asked for by the
// CoSTAR comms team) while the site title still links to the report home.
// The stock NavbarLogo wraps both in a single link.
const COSTAR_URL = 'https://www.costarnetwork.co.uk';

export default function NavbarLogo() {
  const {
    navbar: {title, logo},
  } = useThemeConfig();
  const sources = {
    light: useBaseUrl(logo.src),
    dark: useBaseUrl(logo.srcDark || logo.src),
  };
  return (
    <>
      <a
        className="navbar__brand navbar__brand--logo"
        href={COSTAR_URL}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="CoSTAR National Lab website (opens in a new tab)">
        <ThemedImage
          className="navbar__logo"
          sources={sources}
          height={logo.height}
          width={logo.width}
          alt={logo.alt}
        />
      </a>
      <Link className="navbar__brand" to="/">
        <b className="navbar__title text--truncate">{title}</b>
      </Link>
    </>
  );
}
