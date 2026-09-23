function IconFrame({ children, className = '', viewBox = '0 0 24 24' }) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      focusable="false"
      viewBox={viewBox}
    >
      {children}
    </svg>
  )
}

export function LogoMark({ className = '' }) {
  return (
    <IconFrame className={className} viewBox="0 0 28 32">
      <path
        d="M3 27h7v-8h7v-8h8V3"
        stroke="currentColor"
        strokeLinecap="square"
        strokeLinejoin="miter"
        strokeWidth="4"
      />
    </IconFrame>
  )
}

export function HomeIcon({ className = '' }) {
  return (
    <IconFrame className={className}>
      <path
        d="m4 10 8-6 8 6v9a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </IconFrame>
  )
}

export function PathIcon({ className = '' }) {
  return (
    <IconFrame className={className}>
      <path
        d="m4 17 5-5 3 3 7-8M14 7h5v5"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </IconFrame>
  )
}

export function HistoryIcon({ className = '' }) {
  return (
    <IconFrame className={className}>
      <circle
        cx="12"
        cy="12"
        r="8"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <path
        d="M12 7v5l3 2"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </IconFrame>
  )
}

export function CheckIcon({ className = '' }) {
  return (
    <IconFrame className={className}>
      <circle cx="12" cy="12" r="10" fill="currentColor" />
      <path
        d="m7.8 12.1 2.7 2.7 5.8-6"
        stroke="white"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
      />
    </IconFrame>
  )
}

export function CodeIcon({ className = '' }) {
  return (
    <IconFrame className={className}>
      <path
        d="m9 7-5 5 5 5m6-10 5 5-5 5m-2-12-3 14"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </IconFrame>
  )
}

export function DocumentIcon({ className = '' }) {
  return (
    <IconFrame className={className}>
      <path
        d="M7 3h7l4 4v14H7z"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
      <path
        d="M14 3v5h4M10 12h5m-5 4h5"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
    </IconFrame>
  )
}

export function ArrowRightIcon({ className = '' }) {
  return (
    <IconFrame className={className}>
      <path
        d="M5 12h14m-5-5 5 5-5 5"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </IconFrame>
  )
}

export function ChevronDownIcon({ className = '' }) {
  return (
    <IconFrame className={className}>
      <path
        d="m7 9 5 5 5-5"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </IconFrame>
  )
}
