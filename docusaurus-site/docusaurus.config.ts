import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Multisensory Hub',
  tagline: 'Exploring the science of multisensory experiences',
  favicon: 'img/favicon.svg',

  future: {
    v4: true,
  },

  url: 'https://multisensory.costarnetwork.co.uk',
  baseUrl: '/',

  organizationName: 'costar-national-lab',
  projectName: 'multisensory-hub',

  trailingSlash: false,

  customFields: {
    analyticsReportName: 'Multisensory Hub_Aug',
    // Injected by docx_to_mdx.py on each pipeline run — do not edit manually.
    analyticsManifestVersion: '45669b3b4f92',
  },

  onBrokenLinks: 'warn',
  markdown: {
    format: 'mdx',
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/', // Serve docs at root
          sidebarPath: './sidebars.ts',
          editUrl: undefined, // Remove edit links
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      require.resolve('@cmfcmf/docusaurus-search-local'),
      {
        // Options here
        indexDocs: true,
        indexDocSidebarParentCategories: 3,
        indexBlog: false,
        indexPages: false,
        language: "en",
        lunr: {
          // Optimization for large documents
          tokenizerSeparator: /[\s\-]+/,
        },
      },
    ],
  ],

  themeConfig: {
    image: 'img/social-card.jpg',
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Multisensory Hub',
      logo: {
        alt: 'CoSTAR',
        src: 'img/costar-logo.svg',
        srcDark: 'img/costar-logo-white.svg',
        width: 122,
        height: 30,
      },
      hideOnScroll: false,
      items: [
        {
          type: 'search',
          position: 'right',
        },
      ],
    },
    // NB: the footer is swizzled (src/theme/Footer) — this config block is unused.
    footer: {
      style: 'dark',
      copyright: `Multisensory Hub`,
    },
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
