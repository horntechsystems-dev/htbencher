import{c as i,a as s,o as n,b as t,q as c,e as r,t as a,H as o,B as l}from"./index-Bv8Fydds.js";/**
 * @license lucide-vue-next v0.563.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const b=i("arrow-left",[["path",{d:"m12 19-7-7 7-7",key:"1l729n"}],["path",{d:"M19 12H5",key:"x3x0zl"}]]),d={class:"rounded-lg border bg-surface-white p-6 shadow-sm ring-1 ring-outline-gray-2"},m={class:"flex items-center justify-between"},u={class:"text-sm font-medium text-ink-gray-5"},x={class:"mt-2 flex items-baseline gap-2"},g={class:"text-2xl font-bold tracking-tight text-ink-gray-9"},y={__name:"StatsCard",props:{label:String,value:[String,Number],icon:Object,trend:Number},setup(e){return(h,k)=>(n(),s("div",d,[t("div",m,[t("p",u,a(e.label),1),e.icon?(n(),c(o(e.icon),{key:0,class:"h-4 w-4 text-ink-gray-4"})):r("",!0)]),t("div",x,[t("h3",g,a(e.value),1),e.trend!==void 0?(n(),s("span",{key:0,class:l(["text-xs font-medium",[e.trend>=0?"text-ink-green-3":"text-ink-red-3"]])},a(e.trend>=0?"+":"")+a(e.trend)+"% ",3)):r("",!0)])]))}};export{b as A,y as _};
//# sourceMappingURL=StatsCard-HpqUBrTT.js.map
