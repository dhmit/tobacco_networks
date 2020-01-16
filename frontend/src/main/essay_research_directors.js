import React from 'react';
//import PropTypes from 'prop-types';
import MainLayout from "./main_layout"

import {EssayView, EssaySideNote} from "./essay";

class ResearchDirectorsEssayView extends React.Component {
    constructor(props){
        super(props);
    }


    render(){

        const introduction =
            <>
                <p>
                    The Argentinian researcher Angel Roffo identified carcinogens in smoke as early
                    as the 1930s, and by the 1940s tobacco companies had begun to discuss tobacco
                    as a potential carcinogen.
                    <EssaySideNote content='Proctor, Robert N. Golden Holocaust: Origins of the
                    Cigarette Catastrophe and the Case for Abolition. 1st ed., University of
                    California Press, 2011, p. 16.' />

                    However, the public remained largely
                    unaware of the true health implications of smoking, as key figures within the
                    tobacco industry collaboratively strove to protect the industry’s hold on its
                    consumers. The directors of research at Brown & Williamson (B&W), R. J. Reynolds
                    (RJR), Philip Morris (PM), and Lorillard (LL), were among the major figures
                    associated with the tobacco industry and played significant roles in shaping
                    the focus of research funded by the tobacco industry. They pushed for the
                    funding of research used to distract consumers and raised doubts regarding
                    experiments that showed results linking smoking to harmful health impacts. In
                    this way, the industry’s research directors successfully concealed proof of
                    smoking’s health hazards from the American public until 2000, when Philip
                    Morris,
                    the world&apos;s largest transnational tobacco company, released a statement
                    admitting “an overwhelming medical and scientific consensus that cigarette
                    smoking causes lung cancer, heart disease, emphysema and other serious disease
                    in smokers”
                    <EssaySideNote content='Cummings, K M. “A promise is a promise.” Tobacco control
                    vol. 12,2 (2003): 117-8. doi:10.1136/tc.12.2.117' />
                    on their website.
                </p>
                <h2>Our Project: A Force-Directed Network Graph to Identify Major Players</h2>
                <p>
                    We extracted data about the authors and recipients of 1.4 million documents
                    from the 1970s, including letters, reports, and memos that were sent and
                    received by persons associated with the tobacco industry like executives and
                    lawyers but also academic researchers hired as consultants. By computing a
                    force-directed network graph, we visualized the connections between key
                    researchers at the companies mentioned above. Implemented as an interactive web
                    application, this enabled us to identify several research directors who were
                    highly connected in the network.
                </p>
            </>;

        const essay_content =
            <>
                <section>
                    <p>
                        Among these research directors, Ivor Wallace Hughes (B&W), Murray Senkus
                        (RJR),
                        Helmut Wakeham (PM), and Alexander White Spears (LL), appeared to have had
                        the
                        greatest number of connections. Further investigation reveals that indeed
                        they
                        were key figures and wielded significant influence over the actions of
                        tobacco
                        research and the tobacco industry, demonstrating the power of our network
                        visualizations in identifying crucial players and connections in the tobacco
                        industry. We searched for documents these research directors wrote in the
                        database and determined several strategies they used to foster doubt about
                        the
                        validity of scientific evidence linking smoking and cancer and to distract
                        consumers from rising concern over the health impact of tobacco. These
                        strategies included setting up new research institutions to propagate the
                        tobacco industry’s goals, manipulating existing scientific research
                        agencies,
                        and challenging the science behind experiments that reported results linking
                        health concerns with smoking.
                    </p>
                </section>
                <section>
                    <h2>Creation of Research Institutions: The Council for Tobacco
                        Research (CTR)</h2>
                    <p>
                        A major strategy taken by research directors was to set up research agencies
                        to advance the industry’s own benefit. The main vehicle to carry out this
                        strategy was the Council for Tobacco Research (CTR), which was formed by
                        CEOs of America’s biggest tobacco companies and PR firm Hill & Knowlton to
                        advance the interests of the tobacco industry rather than to meaningfully
                        add to existing literature linking its products to consumer health outcomes.
                        In other words, the CTR’s ultimate goal was to prevent or discredit
                        research studies linking smoking to disease. Its mantra: Not Yet Proven.
                        <EssaySideNote content='Proctor, Robert N. Golden Holocaust: Origins of the
                        Cigarette Catastrophe and the Case for Abolition. 1st ed., University of
                        California Press, 2011, p. 16f.' />
                    </p>
                    <p>
                        Documents from Ivor Wallace Hughes and Helmut Wakeham provide first-hand
                        evidence that demonstrate the true motivations of CTR. Wakeham was the Vice
                        President for Research and Development at Philip Morris and
                        has been called “the most powerful researcher at the world’s most powerful
                        tobacco company.”
                        <EssaySideNote content='Proctor, Robert N. Golden Holocaust: Origins of the
                        Cigarette Catastrophe and the Case for Abolition. 1st ed., University of
                        California Press, 2011, p. 298.' />
                        In a revealing document Wakeham wrote in
                        1970 to Joseph F. Cullman III, the chairman of the company, Wakeham admitted
                        “CTR and the Industry have publicly and frequently denied what others find
                        as ‘truth’”. He wrote candidly, “Let’s face it. We are interested in
                        evidence which we believe denies the allegation that cigarette smoking
                        causes
                        disease”. He acknowledged “both lawyers and scientists will agree...trying
                        to prove that cigaret smoking does not cause disease [would be] extremely
                        difficult”. Hughes, the director of research and development at Brown &
                        Williamson in 1970 (who later became the chairman and CEO of B&W), expressed
                        similar sentiments in one document in 1970, in which he called for
                        “reshaping the CTR...to achieve a research program more pertinent to the
                        industry’s need,”
                        <EssaySideNote
                            content='Hughes, Ivor Wallace, "B&W Effort to Reshape the CTR," June 5,
                             1970.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=zygn0050'
                        />
                        providing further evidence that the
                        public appearance of CTR was a front, with its underlying purpose to
                        advance the goals of the industry rather than act as an objective scientific
                        research council with the health of its consumers in mind.
                    </p>
                </section>
                <section>
                    <h2>Manipulation of Research Institutions</h2>
                    <p>
                        Besides the CTR, research directors also manipulated scientific research in
                        other ways to protect the industry. For example, research directors built
                        relationships with personnel within institutions, effectively creating
                        insiders that would advance the industry’s interests. For example, Huges
                        communicated closely with Gio Gori, a deputy director at NCI’s Division of
                        Cancer Cause and Prevention. As the industry’s ally at NCI, Gori in 1976 and
                        after still claimed that smoking twenty or more Carlton cigarettes (a type
                        of “low-tar” cigarette) per day would not increase the risk of disease, and
                        in 1980, Gori left the NCI with a $400,000 endowment from B&W.
                        <EssaySideNote content='Proctor, Robert N. Golden Holocaust: Origins of the
                        Cigarette Catastrophe and the Case for Abolition. 1st ed., University of
                        California Press, 2011, p. 37.' />
                    </p>
                    <p>
                        When research studies resulted in conclusions that would negatively impact
                        sales or the reputation of the tobacco industry, research directors
                        attempted to prevent these results from becoming widespread. This can be
                        seen in documents written by Alexander White Spears, who was a research
                        associate at Lorillard Tobacco Company and eventually became the CEO and
                        chairman.
                        <EssaySideNote
                            content='Spears, Alexander White, "Resume."'
                            url='https://www.industrydocuments.ucsf.edu/docs/mpxj0015'
                        />
                        In 1960 Spears wrote to
                        John W. Lowell, a chemistry professor at Wake Forest College, and alerted
                        Lowell of the industry’s “recent decision [that] in the interest of the
                        Company and the tobacco industry, [papers that concern] compounds
                        controversial in the health aspects of smoking should not be presented.”
                        <EssaySideNote
                            content='Spears, Alexander White, "Letter to John Lowell," August 17,
                            1960.'
                            url='https://www.industrydocuments.ucsf.edu/docs/gzjk0154'
                        />

                    </p>
                    <p>
                        In another document from 1974, Spears acknowledged the true value of tobacco
                        research to the industry:
                    </p>
                    <blockquote cite="https://www.industrydocuments.ucsf.edu/docs/sxjf0110">
                        <p>
                            Historically, the joint industry funded smoking and health research
                            programs
                            have not been selected against specific scientific goals, but rather for
                            various purposes such as public relations, political relations, position
                            for
                            litigation, etc...In general, these programs have provided some buffer
                            to
                            the public and political attack of the industry, as well as background
                            for
                            litigious strategy.
                        </p>
                        <footer><a href="https://www.industrydocuments.ucsf.edu/docs/sxjf0110">
                            Spears, Alexander White, III. &quot;Memorandum,&quot; June 24, 1974.</a>
                        </footer>
                    </blockquote>
                    <p>
                        Like other research directors, Spears saw tobacco research as a way to
                        distract and mislead the public to the advantage of the industry. Statements
                        like Spears’s above serve to remind us just how explicit some of the
                        documents we analyzed were in regard to the goals and motivations of the
                        tobacco industry given their public statement that there was a real
                        controversy about smoking’s health harms. Many actions that individuals in
                        the industry took that were once unknown or shrouded in secrecy are now
                        open to the public and to analysis, and the discoveries yielded have been
                        eye-opening– if not shocking.
                    </p>
                </section>
                <section>
                    <h2>Challenging the Validity of Experiments</h2>
                    <p>
                        Another strategy research directors adopted was to challenge scientific
                        experiments that demonstrated the negative effects of tobacco on health.
                        For example, Hughes wrote a note in 1974 to criticize the National Cancer
                        Institute (NCI) report on the relationship between nicotine and
                        tumorigenicity. He claimed that “although the correlations are strong…
                        there is no strong scientific basis for concluding that the level of
                        nicotine in tobacco is related to tumorigenicity.” He argued that strong
                        correlations are not necessarily causes, that the experiments were not
                        designed to specifically examine the effect of nicotine, that many unknown
                        variables were present, and that previous unpublished experiments by the
                        CTR showed contrary indications to those found in the NCI report.
                        <EssaySideNote
                            content='Hughes, Ivor Wallace, "Note Re: Relation between Nicotine and
                            Tumorigenicity," July 22, 1974.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=jggn0050'
                        />
                    </p>
                    <p>
                        In another letter Hughes co-authored with other research directors
                        (including Murray Senkus and Helmut Wakeham) in 1972, he objected to NCI’s
                        proposed dog inhalation experiments on the effects of nicotine by claiming
                        the “use of tracheostomy for introducing smoke directly into the dogs’
                        lungs is much too artificial, traumatic and stressful”, and “the chemical
                        composition of the smoke as received directly into the pulmonary system of
                        the dogs will differ radically from that ordinarily inhaled by humans”
                        <EssaySideNote
                            content='Bates, William Wannamaker, Ivor Wallace Hughes,
                            Murray Senkus, Alexander White Spears, Helmut Wakeham, "Letter, re:
                             Objections to proposed dog inhalation experiment funded by National
                             Cancer Institute," March 24, 1972.'
                            url="https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=mfhv0035"
                        />
                        Ironically, these criticisms on NCI’s experiments were sent
                        to Gio Gori, the deputy director at NCI who acted as an ally to the
                        industry.
                    </p>
                    <p>
                        Similar to Hughes, Murray Senkus, the director of chemical research at
                        Reynolds, also made criticisms on various experiments that
                        demonstrated the health hazards of smoking.
                        <EssaySideNote content='Proctor, Robert N. Golden Holocaust: Origins of the
                        Cigarette Catastrophe and the Case for Abolition. 1st ed., University of
                        California Press, 2011, p. 196.' />
                        For example, in a letter Senkus
                        wrote in 1976 that discussed issues with the FTC lab’s experiments on
                        effects of smoking, he called their carbon monoxide analysis “inherently
                        inaccurate” and claimed the data complexity “increase[s] the opportunity
                        for human error” and that the data collected was not “applicable to all
                        brands and cigarette types”
                        (Senkus, Letter from Murray Senkus to Allan J Topol 2).
                    </p>
                </section>
                <section>
                    <h2>Improving Reputation of the Industry by Funding Research</h2>
                    <p>
                       Besides the tactics of criticizing experimental procedures, Senkus also
                        attempted to establish research funds at universities to build the
                        credibility of the tobacco industry. One document revealed he
                        “wholeheartedly endorse establishment of an R. J. Reynolds Industries Fund
                        at MIT”, with the goal being to “discharge our obligation of a corporate
                        citizen” and “assure our credibility in the scientific community.”
                        (Senkus, Proposal for Establishment of RJ Reynolds Industries Fund 3)
                    </p>
                    <p>
                        The CTR provides another example of ostensibly supporting scientific
                        research to improve the industry’s reputation. For instance, Wakeham
                        considered that by aiming CTR to search for causes of diseases, this
                        would demonstrate the industry’s interest in “human welfare and alleviation
                        of human suffering”, and that therefore “the public should love and respect
                        us and buy our products”.
                        <EssaySideNote
                            content='Wakeham, Helmut, "Best Program for C.T.R," December 8, 1970.'
                            url='https://www.industrydocuments.ucsf.edu/docs/#id=ymkp0124'
                        />

                    </p>
                </section>
                <section>
                    <h2>Summary</h2>
                    <p>
                        Our force directed graph extracted data from more than 11.3 million
                        documents relating to the tobacco industry, many of which were internal and
                        previously classified. It only takes a few glances at some of these
                        documents to realize that their initial confidentiality of these documents
                        was for good reason; many of these documents are particularly incriminating.
                        They contain blunt acknowledgements from powerful individuals in the tobacco
                        industry about the industry’s unofficial goals of distracting and deceiving
                        consumers about the health hazards of smoking. And with the help of our
                        force directed graph, we were able to understand just how much pull such
                        individuals had within the tobacco industry’s network.
                    </p>
                </section>
            </>;


        const content =
            <EssayView
                title='The Smokescreen'
                subtitle='How the Research Directors of American Cigarette Makers
                Deceived the American Public About the Health Hazards of Smoking'
                epigraph={null}
                introduction={introduction}
                authors='Raquel Garcia, Christina Wang, Angel Yang'
                dataset_name='research_directors'
                essay_content={essay_content}
            />;

        return(
            <MainLayout
                content={content}
            />

        )
    }
}

export default ResearchDirectorsEssayView;
