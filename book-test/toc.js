// Populate the sidebar
//
// This is a script, and not included directly in the page, to control the total size of the book.
// The TOC contains an entry for each page, so if each page includes a copy of the TOC,
// the total size of the page becomes O(n**2).
class MDBookSidebarScrollbox extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded affix "><a href="introduction.html">Introduction</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Foundational Documents</li><li class="chapter-item expanded "><a href="other/1974-City-Charter.html"><strong aria-hidden="true">1.</strong> City Charter (1974)</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Ordinances</li><li class="chapter-item expanded "><a href="ordinances/1974-Ord-16-Parks.html"><strong aria-hidden="true">2.</strong> #16 Park Advisory (1974)</a></li><li class="chapter-item expanded "><a href="ordinances/1978-Ord-28-Parks.html"><strong aria-hidden="true">3.</strong> #28 Park Council (1978)</a></li><li class="chapter-item expanded "><a href="ordinances/1987-Ord-52-Flood.html"><strong aria-hidden="true">4.</strong> #52 Flood Prevention (1987)</a></li><li class="chapter-item expanded "><a href="ordinances/1989-Ord-54-89C-Land-Development.html"><strong aria-hidden="true">5.</strong> #54 Land Development (1989)</a></li><li class="chapter-item expanded "><a href="ordinances/1993-Ord-57-93-Manufactured-Homes.html"><strong aria-hidden="true">6.</strong> #57 Manufactured Homes (1993)</a></li><li class="chapter-item expanded "><a href="ordinances/1998-Ord-59-97A-Land-Development-Amendment.html"><strong aria-hidden="true">7.</strong> #59 Lot Standards (1998)</a></li><li class="chapter-item expanded "><a href="ordinances/1998-Ord-61-98-Land-Development-Amendment.html"><strong aria-hidden="true">8.</strong> #61 Flood Districts (1998)</a></li><li class="chapter-item expanded "><a href="ordinances/1998-Ord-62-98-Flood-and-Land-Development-Amendment.html"><strong aria-hidden="true">9.</strong> #62 Flood Prevention (1998)</a></li><li class="chapter-item expanded "><a href="ordinances/1999-Ord-65-99-Sewer-Services.html"><strong aria-hidden="true">10.</strong> #65 Sewer Services (1999)</a></li><li class="chapter-item expanded "><a href="ordinances/2000-Ord-68-2000-Metro-Compliance.html"><strong aria-hidden="true">11.</strong> #68 Metro Compliance (2000)</a></li><li class="chapter-item expanded "><a href="ordinances/2000-Ord-69-2000-Title-3-Compliance.html"><strong aria-hidden="true">12.</strong> #69 Title 3 Compliance (2000) [NEVER PASSED]</a></li><li class="chapter-item expanded "><a href="ordinances/2001-Ord-70-2001-WQRA.html"><strong aria-hidden="true">13.</strong> #70 Water Quality (2001)</a></li><li class="chapter-item expanded "><a href="ordinances/2002-Ord-71-2002-Gates.html"><strong aria-hidden="true">14.</strong> #71 Gates Prohibited (2002)</a></li><li class="chapter-item expanded "><a href="ordinances/2002-Ord-72-2002-Penalties-and-Abatement-Amendment.html"><strong aria-hidden="true">15.</strong> #72 Penalties (2002)</a></li><li class="chapter-item expanded "><a href="ordinances/2003-Ord-73-2003A-Conditional-Use-Provisions.html"><strong aria-hidden="true">16.</strong> #73 Conditional Uses (2003)</a></li><li class="chapter-item expanded "><a href="ordinances/2004-Ord-74-2004-Tree-Cutting-Amendment.html"><strong aria-hidden="true">17.</strong> #74 Tree Cutting (2004)</a></li><li class="chapter-item expanded "><a href="ordinances/2008-Ord-76-2008-FEMA-Flood-Map.html"><strong aria-hidden="true">18.</strong> #76 Flood Maps (2008)</a></li><li class="chapter-item expanded "><a href="ordinances/2011-Ord-80-2011-Park-Hours.html"><strong aria-hidden="true">19.</strong> #80 Park Hours (2011)</a></li><li class="chapter-item expanded "><a href="ordinances/2011-Ord-81-2011-Sign.html"><strong aria-hidden="true">20.</strong> #81 Sign Regulations (2011)</a></li><li class="chapter-item expanded "><a href="ordinances/2017-Ord-88-2017-Docks.html"><strong aria-hidden="true">21.</strong> #88 Dock Regulations (2017)</a></li><li class="chapter-item expanded "><a href="ordinances/2018-Ord-89-2018-Tree-Cutting-Amendment.html"><strong aria-hidden="true">22.</strong> #89 Tree Protection (2018)</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Resolutions</li><li class="chapter-item expanded "><a href="resolutions/1976-Res-22-PC.html"><strong aria-hidden="true">23.</strong> #22 Citizen Involvement (1976)</a></li><li class="chapter-item expanded "><a href="resolutions/1984-Res-72-Municipal-Services.html"><strong aria-hidden="true">24.</strong> #72 Municipal Services (1984)</a></li><li class="chapter-item expanded "><a href="resolutions/2018-Res-256-Planning-Development-Fees.html"><strong aria-hidden="true">25.</strong> #256-2018 Development Fees (2018) [SUPERSEDED]</a></li><li class="chapter-item expanded "><a href="resolutions/2018-Res-259-Planning-Development-Fees.html"><strong aria-hidden="true">26.</strong> #259-2018 Development Fees (2018) [SUPERSEDED]</a></li><li class="chapter-item expanded "><a href="resolutions/2019-Res-265-2019.html"><strong aria-hidden="true">27.</strong> #265-2019 Admin Rules (2020) [NEVER PASSED]</a></li><li class="chapter-item expanded "><a href="resolutions/2024-Res-300-Fee-Schedule-Modification.html"><strong aria-hidden="true">28.</strong> #300-2024 Development Fees (2024)</a></li><li class="chapter-item expanded "><a href="resolutions/2019-Res-41425-Public-Records.html"><strong aria-hidden="true">29.</strong> #41425 Public Records (2025)</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Planning Commission Interpretations</li><li class="chapter-item expanded "><a href="interpretations/1997-07-07-RE-2.040h-permitting-adus.html"><strong aria-hidden="true">30.</strong> Accessory Structures (1997-07-07)</a></li><li class="chapter-item expanded "><a href="interpretations/1997-09-08-RE-9.030-permit-fees-and-completeness.html"><strong aria-hidden="true">31.</strong> Permit Fees (1997-09-08)</a></li><li class="chapter-item expanded "><a href="interpretations/1997-11-03-RE-9.030-permit-fees-and-completeness.html"><strong aria-hidden="true">32.</strong> Development Charges (1997-11-03)</a></li><li class="chapter-item expanded "><a href="interpretations/1998-03-02-RE-5.080-setbacks.html"><strong aria-hidden="true">33.</strong> Setback Measurement (1998-03-02)</a></li><li class="chapter-item expanded "><a href="interpretations/1998-06-01-RE-5.080-setback-orientation.html"><strong aria-hidden="true">34.</strong> Setback Orientation (1998-06-01)</a></li><li class="chapter-item expanded "><a href="interpretations/1998-07-06-RE-5.080-setback-orientation.html"><strong aria-hidden="true">35.</strong> Building Setbacks (1998-07-06)</a></li><li class="chapter-item expanded "><a href="interpretations/2001-05-07-RE-balanced-cut-and-fill.html"><strong aria-hidden="true">36.</strong> Bankful Stage (2001-05-07)</a></li><li class="chapter-item expanded "><a href="interpretations/2002-08-05-RE-lots-partially-in-floodplain.html"><strong aria-hidden="true">37.</strong> Floodplain Lots (2002-08-05)</a></li><li class="chapter-item expanded "><a href="interpretations/2002-09-05-RE-duplicate.html"><strong aria-hidden="true">38.</strong> Floodplain Lots (2002-09-05)</a></li><li class="chapter-item expanded "><a href="interpretations/2004-10-11-RE-5.080-setbacks.html"><strong aria-hidden="true">39.</strong> Wqra Setbacks (2004-10-11)</a></li><li class="chapter-item expanded "><a href="interpretations/2005-04-04-RE-adu-sewer.html"><strong aria-hidden="true">40.</strong> Sewer Permits (2005-04-04)</a></li><li class="chapter-item expanded "><a href="interpretations/2008-02-04-RE-multi-family.html"><strong aria-hidden="true">41.</strong> Multi-Family (2008-02-04)</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Council Meetings</li><li class="chapter-item expanded "><a href="agendas/2018-04-11-Agenda.html"><strong aria-hidden="true">42.</strong> 2018-04-10 - Agenda</a></li><li class="chapter-item expanded "><a href="agendas/2018-05-14-Agenda.html"><strong aria-hidden="true">43.</strong> 2018-05-13 - Agenda</a></li><li class="chapter-item expanded "><a href="minutes/2017-06-12-Minutes.html"><strong aria-hidden="true">44.</strong> 2017-06-11 - Minutes</a></li><li class="chapter-item expanded "><a href="minutes/2017-11-13-Minutes.html"><strong aria-hidden="true">45.</strong> 2017-11-12 - Minutes</a></li><li class="chapter-item expanded "><a href="minutes/2018-08-13-Minutes.html"><strong aria-hidden="true">46.</strong> 2018-08-12 - Minutes</a></li><li class="chapter-item expanded "><a href="minutes/2018-12-10-Minutes.html"><strong aria-hidden="true">47.</strong> 2018-12-09 - Minutes</a></li><li class="chapter-item expanded "><a href="transcripts/2024-02-12-Transcript.html"><strong aria-hidden="true">48.</strong> 2024-02-11 - Transcript</a></li><li class="chapter-item expanded "><a href="transcripts/2024-12-09-Transcript.html"><strong aria-hidden="true">49.</strong> 2024-12-08 - Transcript</a></li></ol>';
        // Set the current, active page, and reveal it if it's hidden
        let current_page = document.location.href.toString().split("#")[0].split("?")[0];
        if (current_page.endsWith("/")) {
            current_page += "index.html";
        }
        var links = Array.prototype.slice.call(this.querySelectorAll("a"));
        var l = links.length;
        for (var i = 0; i < l; ++i) {
            var link = links[i];
            var href = link.getAttribute("href");
            if (href && !href.startsWith("#") && !/^(?:[a-z+]+:)?\/\//.test(href)) {
                link.href = path_to_root + href;
            }
            // The "index" page is supposed to alias the first chapter in the book.
            if (link.href === current_page || (i === 0 && path_to_root === "" && current_page.endsWith("/index.html"))) {
                link.classList.add("active");
                var parent = link.parentElement;
                if (parent && parent.classList.contains("chapter-item")) {
                    parent.classList.add("expanded");
                }
                while (parent) {
                    if (parent.tagName === "LI" && parent.previousElementSibling) {
                        if (parent.previousElementSibling.classList.contains("chapter-item")) {
                            parent.previousElementSibling.classList.add("expanded");
                        }
                    }
                    parent = parent.parentElement;
                }
            }
        }
        // Track and set sidebar scroll position
        this.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                sessionStorage.setItem('sidebar-scroll', this.scrollTop);
            }
        }, { passive: true });
        var sidebarScrollTop = sessionStorage.getItem('sidebar-scroll');
        sessionStorage.removeItem('sidebar-scroll');
        if (sidebarScrollTop) {
            // preserve sidebar scroll position when navigating via links within sidebar
            this.scrollTop = sidebarScrollTop;
        } else {
            // scroll sidebar to current active section when navigating via "next/previous chapter" buttons
            var activeSection = document.querySelector('#sidebar .active');
            if (activeSection) {
                activeSection.scrollIntoView({ block: 'center' });
            }
        }
        // Toggle buttons
        var sidebarAnchorToggles = document.querySelectorAll('#sidebar a.toggle');
        function toggleSection(ev) {
            ev.currentTarget.parentElement.classList.toggle('expanded');
        }
        Array.from(sidebarAnchorToggles).forEach(function (el) {
            el.addEventListener('click', toggleSection);
        });
    }
}
window.customElements.define("mdbook-sidebar-scrollbox", MDBookSidebarScrollbox);
