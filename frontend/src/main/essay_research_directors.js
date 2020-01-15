import React from 'react';
//import PropTypes from 'prop-types';
import EssayView from "./essay";
import MainLayout from "./main_layout"
import EssaySideNote from "./essay_note"


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
                        (Proctor 16-17).
                    </p>
                    <p>
                        Documents from Ivor Wallace Hughes and Helmut Wakeham provide first-hand
                        evidence that demonstrate the true motivations of CTR. Wakeham was the Vice
                        President for Research and Development at Philip Morris (Proctor 386) and
                        has been called “the most powerful researcher at the world’s most powerful
                        tobacco company” (Proctor 298). In a revealing document Wakeham wrote in
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
                        industry’s need” (Hughes, B&W Effort), providing further evidence that the
                        public appearance of CTR was a front, with its underlying purpose to
                        advance the goals of the industry rather than act as an objective scientific
                        research council with the health of its consumers in mind.
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
