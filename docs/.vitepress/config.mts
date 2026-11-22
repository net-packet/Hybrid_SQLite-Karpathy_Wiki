import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Hybrid Archive',
  description: 'SQLite FTS5 + Karpathy Wiki — bilingual document archive / آرشیو اسناد دوزبانه',
  base: '/Hybrid_SQLite-Karpathy_Wiki/',

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#3c8772' }]
  ],

  locales: {
    root: {
      label: 'English',
      lang: 'en',
      title: 'Hybrid Archive',
      description: 'SQLite FTS5 + Karpathy Wiki document archive',
      themeConfig: {
        nav: [
          { text: 'Guide', link: '/guide/ingest' },
          { text: 'Collections', link: '/collections/office-works' },
          { text: 'CLI', link: '/guide/cli' }
        ],
        sidebar: [
          {
            text: 'Getting Started',
            items: [
              { text: 'Overview (SCHEMA)', link: '/' },
              { text: 'Ingest Workflow', link: '/guide/ingest' }
            ]
          },
          {
            text: 'Reference',
            items: [
              { text: 'CLI Reference', link: '/guide/cli' },
              { text: 'Architecture', link: '/guide/architecture' },
              { text: 'Wiki Layer', link: '/guide/wiki-layer' },
              { text: 'Design Decisions', link: '/guide/design-decisions' },
              { text: 'Skills & Automation', link: '/guide/skills' }
            ]
          },
          {
            text: 'Collections',
            items: [
              { text: 'Office Works', link: '/collections/office-works' },
              { text: 'Maintenance Learning', link: '/collections/maintenance-learning' },
              { text: 'AI Learning', link: '/collections/ai-learning' }
            ]
          }
        ],
        outline: { label: 'On this page' },
        docFooter: { prev: 'Previous', next: 'Next' },
        returnToTopLabel: 'Back to top',
        sidebarMenuLabel: 'Menu',
        darkModeSwitchLabel: 'Appearance'
      }
    },
    fa: {
      label: 'فارسی',
      lang: 'fa-IR',
      dir: 'rtl',
      title: 'آرشیو ترکیبی',
      description: 'آرشیو اسناد دوزبانه SQLite FTS5 + ویکی کارپتی',
      themeConfig: {
        nav: [
          { text: 'راهنما', link: '/fa/guide/ingest' },
          { text: 'مجموعه‌ها', link: '/fa/collections/office-works' },
          { text: 'دستورات', link: '/fa/guide/cli' }
        ],
        sidebar: [
          {
            text: 'شروع',
            items: [
              { text: 'مرور کلی (SCHEMA)', link: '/fa/' },
              { text: 'جریان ingest', link: '/fa/guide/ingest' }
            ]
          },
          {
            text: 'مرجع',
            items: [
              { text: 'دستورات CLI', link: '/fa/guide/cli' },
              { text: 'معماری', link: '/fa/guide/architecture' },
              { text: 'لایه ویکی', link: '/fa/guide/wiki-layer' },
              { text: 'تصمیم‌های طراحی', link: '/fa/guide/design-decisions' },
              { text: 'مهارت‌ها و اتوماسیون', link: '/fa/guide/skills' }
            ]
          },
          {
            text: 'مجموعه‌ها',
            items: [
              { text: 'کارهای اداری', link: '/fa/collections/office-works' },
              { text: 'آموزش نگهداشت', link: '/fa/collections/maintenance-learning' },
              { text: 'آموزش هوش مصنوعی', link: '/fa/collections/ai-learning' }
            ]
          }
        ],
        outline: { label: 'در این صفحه' },
        docFooter: { prev: 'قبلی', next: 'بعدی' },
        returnToTopLabel: 'بازگشت به بالا',
        sidebarMenuLabel: 'منو',
        darkModeSwitchLabel: 'ظاهر'
      }
    }
  },

  themeConfig: {
    logo: { src: '/logo.svg', width: 24, height: 24 },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/net-packet/Hybrid_SQLite-Karpathy_Wiki' }
    ],
    search: {
      provider: 'local',
      options: {
        locales: {
          root: { translations: { button: { buttonText: 'Search', buttonAriaLabel: 'Search' } } },
          fa: { translations: { button: { buttonText: 'جستجو', buttonAriaLabel: 'جستجو' }, modal: { noResultsText: 'نتیجه‌ای پیدا نشد', resetButtonTitle: 'پاک کردن', footer: { selectText: 'انتخاب', navigateText: 'رفتن به', closeText: 'بستن' } } } }
        }
      }
    },
    footer: {
      message: 'Built with Hermes Agent — local-first, privacy-respecting',
      copyright: 'MIT License'
    }
  },

  markdown: {
    lineNumbers: true
  }
})
