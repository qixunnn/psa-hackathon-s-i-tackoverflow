const ports = [[106,104],[137,116],[163,103],[205,129],[257,144],[305,156],[383,143],[455,162],[535,172],[611,171],[679,194],[746,170],[806,190],[861,170],[905,130],[841,103],[760,89],[680,111],[604,128],[517,113],[439,103],[352,98],[277,84],[190,74]]
const routeOne = 'M104 104 C190 58 240 76 305 156 S430 195 535 172 S675 116 746 170 S840 209 905 130'
const routeTwo = 'M137 116 C206 126 238 180 305 156 C387 126 441 91 517 113 C615 143 627 215 746 170 C817 143 850 144 905 130'
const routeThree = 'M104 104 C74 187 163 241 257 214 C346 188 382 175 455 162 C580 142 664 68 760 89 C831 107 857 119 905 130'

export default function MapPanel({ run, viewMode = '2D' }) {
  const riskActive = (run?.risk_assessment?.affected_chokepoints || []).length > 0
  return <section className={`world-map ${viewMode === '3D' ? 'globe-view' : ''}`} aria-label="Global maritime route map">
    <div className="map-glow" />
    <svg viewBox="0 0 1000 430" role="img" aria-label="Global shipping routes and maritime risk zones" preserveAspectRatio="xMidYMid slice">
      <defs><linearGradient id="sea" x1="0" x2="1"><stop stopColor="#07121f"/><stop offset=".6" stopColor="#0a1522"/><stop offset="1" stopColor="#07111b"/></linearGradient><filter id="routeGlow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter><pattern id="grid" width="38" height="38" patternUnits="userSpaceOnUse"><path d="M38 0H0V38" fill="none" stroke="#8aa0b4" strokeOpacity=".045" strokeWidth="1"/></pattern></defs>
      <rect width="1000" height="430" fill="url(#sea)"/><rect width="1000" height="430" fill="url(#grid)"/>
      <g className="continents"><path d="M0 60L52 41 111 53 144 77 167 70 191 101 171 132 132 142 117 169 84 171 61 204 28 193 4 158Z"/><path d="M144 188L188 199 219 239 207 292 184 337 155 315 146 271 124 237Z"/><path d="M354 58L401 41 451 53 492 43 542 61 594 52 642 65 684 56 741 77 785 71 829 96 876 97 929 126 912 154 858 157 823 184 770 173 725 189 677 172 636 191 584 178 550 148 501 158 457 140 420 146 392 120 352 107Z"/><path d="M426 157L491 152 533 182 550 225 526 278 492 321 454 309 433 263 410 207Z"/><path d="M746 226L792 216 826 238 867 245 889 281 860 309 812 304 770 277 735 253Z"/><path d="M912 164L938 151 956 169 944 188 919 190Z"/></g>
      <g className="country-lines"><path d="M70 69L98 112 61 150M137 79L117 169M167 199L183 267 156 315M401 66L420 146M452 54L457 140M501 58L501 158M550 61L550 148M594 52L584 178M642 65L636 191M684 56L677 172M741 77L725 189M785 71L770 173M829 96L823 184M491 152L492 321M433 202L533 182M770 245L860 309"/></g>
      <g className="map-labels"><text x="74" y="120">NORTH AMERICA</text><text x="148" y="260">SOUTH AMERICA</text><text x="417" y="102">EUROPE</text><text x="458" y="234">AFRICA</text><text x="648" y="112">ASIA</text><text x="788" y="271">AUSTRALIA</text><text x="560" y="213">INDIAN OCEAN</text></g>
      <g className="shipping-routes" filter="url(#routeGlow)"><path className="route muted" d={routeTwo}/><path className="route green" d={routeThree}/><path className="route cyan" d={routeOne}/></g>
      <g className="risk-zone"><path d="M493 134L535 152 558 195 521 224 485 180Z"/><circle cx="520" cy="176" r="6"/><text x="528" y="169">HORMUZ WATCH</text></g>
      <g className="port-signals">{ports.map(([x,y], index) => <g key={`${x}-${y}`}><circle className="signal-ring" cx={x} cy={y} r={index % 4 === 0 ? 7 : 4}/><circle cx={x} cy={y} r="2"/></g>)}</g>
      <g className="map-markers"><g transform="translate(300 146)"><circle r="8"/><path d="M-3 0h6M0-3v6"/></g><g transform="translate(744 160)"><circle r="8"/><path d="M-3 0h6M0-3v6"/></g></g>
    </svg>
    <div className="map-coordinate">LAT 01.3521° N&nbsp;&nbsp; LNG 103.8198° E</div>
    <div className={`map-live-state ${riskActive ? 'alert' : ''}`}><span /> {riskActive ? 'RISK OVERLAY ACTIVE' : 'LIVE GLOBAL ROUTE MONITOR'}</div>
  </section>
}
