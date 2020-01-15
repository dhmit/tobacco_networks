import React from 'react';
//import PropTypes from 'prop-types';
import EssayView from "./essay";
import MainLayout from "./main_layout"
import EssaySideNote from "./essay_note"


class SterlingEssayView extends React.Component {
    constructor(props){
        super(props);
    }


    render(){

        const epigraph = {
            'content': 'There are three types of lies: lies, damned lies, and statistics.',
            'author': 'Mark Twain'
        };

        const introduction =
            <>
                <p>
                    In many respects, the tobacco industry’s rise and continued success long
                    after the harmful effects of cigarettes were understood by researchers had
                    to do with a few select researchers , lawyers, and industry spokespeople who
                    supported the industry and worked to obfuscate the truth about  smoking’s
                    health harms. How did these researchers operate? How did they use scientific
                    rhetoric and evidence to produce ignorance instead of knowledge? This essay
                    uses one of the industry’s favorite guns for hire, Theodor Sterling, to
                    explore these questions. Theodor Sterling, also known as Ted Sterling, was
                    a professor of statistics and computing who held several academic and
                    professorial positions across colleges in the United States, including
                    Director of the Computing Center at the University of Cincinnati.
                    <EssaySideNote
                        content="Stanton Glantz, John Slade et. al. The Cigarette
                        Papers. Berkeley: University of California Press, 1996, p. 296-301."
                    />
                    There he
                    combined statistics and computer science in biomedical research. Sterling’s
                    access to mainframe computers via his workplace allowed for his side
                    business, a small consulting firm called Theodor D Sterling & Associates
                    (TDS, also referred to as TDS&A, TDS Ltd., TDSA) to thrive at a time in
                    history when computing power was both rare and costly.
                </p>
                <p>
                    Sterling’s success was also due in part to his willingness to work for anyone,
                    which quickly made his research services into a great asset for the tobacco
                    industry. From 1968 to 1990, he worked for the Council for Tobacco Research
                    (CTR) on nine different Special Projects (which were really just a front for
                    the CTR to pay its most trusted allies since these did not have to go through
                    the CTR’s Scientific Advisory Board), pocketing a total of $5,560,210 for his
                    troubles. Additionally, Sterling worked directly for the tobacco companies and
                    the law firms representing them, so it is likely that he received more than $10
                    million in total.
                    <EssaySideNote
                        content="Stephan Risi. Manufacturing Doubt Distraction and Subversion
                        Research at the Council for Tobacco Research"
                        url="http://tobacco-analytics.org/case/ctr"
                    />
                    As a result, TDS grew to be one of the most significant
                    contributors of fake scientific documents playing down the harms of smoking and
                    tobacco-use from the early 1960s and up until the 1990s.
                </p>
            </>;

        const essay_content =
            <>
                <section>
                    <h2>What kind of research and special projects would be worth such a large
                        amount
                        of money?</h2>
                    <p>
                        Ted Sterling spent much of his career researching causes of lung cancer
                        other
                        than smoking, arguing that soot, as well as social class and occupational
                        hazards, were more significant factors in causing lung cancer than smoking.
                        In his career, Sterling prolifically worked with data collection and
                        analysis
                        procedures. Often, Sterling used his experience with statistics to argue
                        against
                        National Health Survey data and other scientific findings on the basis of
                        supposedly invalid data sampling and analysis. For instance, in response to
                        a
                        so called “morbidity report” published in May 1967 by the Public Health
                        Service
                        which suggested a link between cigarettes and cancer, Sterling was quoted
                        expressing his clear opposition.
                        <EssaySideNote
                            content="National Center for Health Statistics: Cigarette
                            Smoking and Health Characteristics, United States, July 1964-June 1965.
                            Vital and Health Statistics 10, No. 34 (Hyattsville, MD), May 1967."
                        />
                         He stated “the report on cigarette smoking and
                        health characteristics is based on most uncertain and inaccurate data, it is
                        based on very in-adequate analytic procedures, and it lacks conviction that
                        it
                        really demonstrates any difference between smokers and nonsmokers.”
                        <EssaySideNote
                            content="Anonymous, 1970, p. 26."
                            url="https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=jnbh0137"
                        />
                         It was
                        sentiments like this that helped fuel the growing movement against
                        cigarettes
                        as a cause of cancer. In another case, when E. Cuyler Hammond produced a
                        study
                        on the increased death rates caused by smoking in one million men and women
                        in
                        1966, Sterling received $57,865 to express his “enormous doubts about the
                        validity of National Health Survey Data conclusions,” (those doubts being
                        expressed most importantly in front of the Congressional Committee on Public
                        Works  in 1968).
                        <EssaySideNote
                            content="“Special Project Number 51, 51S. Feasibility of a Definitive
                            Evaluation of the Data Concerning Smoking and General Morbidity and
                            Disability.”"
                            url="https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=tkjd0024"
                        />
                        Through these examples, and countless others, it becomes
                        clear that the work of Ted Sterling in support of the Tobacco Industry was
                        primarily motivated by a desire for personal wealth. However, the
                        consequences
                        of his work were felt universally and served to ambiguate the truth and
                        prolong
                        the harms of cigarette smoking for decades.
                    </p>
                    <p>
                        Another important feature of Sterling’s research was his objective to
                        delegitimize the known dangers of second-hand smoking. Funded by Council for
                        Tobacco Research (CTR), he went to extensive efforts to find potential
                        causes
                        of lung cancer that wouldn’t pose a threat to the power of Big Tobacco,
                        namely
                        indoor air pollution. While working for the University of Cincinnati in
                        March
                        of 1965, Ted Sterling went on record before the Senate Committee on Commerce
                        to
                        state that no true verdict had been reached regarding whether cigarette
                        smoke
                        could cause cancer, claiming “the results of all [animal studies which
                        attempted
                        to produce lung cancer by means of cigarette smoke] have been negative.”
                        <EssaySideNote content="United States. Congress. Senate. Committee on
                        Commerce.
                        Cigarette Labeling And Advertising: Hearings, Eighty-ninth Congress, First
                        Session. Washington: U. S. Government Printing Office, 1965." />
                        Later
                        in this session, he condemned other researchers’ “criteria for scientific
                        proof”
                        in an effort to guard his statement against scientific “interpretations”
                        that
                        showed any correlation between cigarette smoke and disease. Simply put, Ted
                        Sterling helped generate doubt about the negative impacts of tobacco usage
                        by
                        running his own experiments and testifying against the validity of other
                        scientific research that might have hurt the tobacco companies.
                    </p>
                </section>
                <section>
                    <h2>Moving the bar: How Sterling argued that there was still doubt about
                        smoking’s link to lung cancer</h2>
                    <p>
                        Despite getting paid large sums of money for research into other causes of
                        lung cancer, many of Sterling’s claims lacked firm scientific backing,
                        research, and experiments. Rather, he relied heavily on his credibility as
                        a statistician and academic to back his ideas and counterclaims. Most of the
                        jobs that the CTR assigned to Sterling were explicit attempts to discredit
                        and invalidate research that tried to link smoking as a cause of lung
                        cancer. His career as a statistician gave credence to his ability to argue
                        against the statistical methods and practices that other researchers were
                        using at the time.
                    </p>
                    <p>
                        Sterling’s criticisms of other research were often merely attacks on the
                        researchers themselves or petty criticisms of their methods. For example,
                        in his response to the 1964 Surgeon General’s Report,
                        <EssaySideNote
                            content="Theodor Sterling. “An Evaluation and Review of the Report on
                            Smoking and Health by the Advisory Committee to the Surgeon General.”
                            March 1964."
                            url="https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=nnkp0215"
                        />
                        “Sterling took issue
                        with the fact that the Surgeon General was ready to close the case and try
                        to save lives even if he was only 99.9% sure that smoking caused cancer. A
                        real scientist, he seems to argue, would have waited another twenty years
                        to root out the remaining 0.1%.”
                        <EssaySideNote
                            content="Stephan Risi. Manufacturing Doubt Distraction and Subversion
                            Research at the Council for Tobacco Research"
                            url="http://tobacco-analytics.org/case/ctr"
                        />
                        In all likelihood, no amount of poof would
                        have satisfied Sterling because that would mean closing the case, which is
                        the opposite of what the tobacco industry wanted. Rather, Sterling would
                        have increased his scrutiny of other research and what constituted a causal
                        relationship so that he could always say that there was still room for doubt
                        about the harmful effects of smoking.
                    </p>
                    <p>
                        This statement exemplifies a lot about Sterling’s supposed beliefs and
                        research. He could not truly provide evidence countering the claims against
                        smoking and its negative effects, so rather he had to argue against the
                        methods that led to those results and how statistically significant those
                        results were. Such claims now seem to be preposterous and we might wonder
                        how they could ever be believed, but at the time, a lot of the research that
                        was being released was very new and ran contrary to what many people
                        believed. Considering the fact that Sterling had a reputation and career
                        based on statistical analysis, his claims didn’t seem so absurd and likely
                        actually appealed to many peoples’ confirmation bias.
                    </p>
                    <p>
                        The CTR was pleased with many of his congressional hearings and papers which
                        merely contested other researcher’s evidence instead of introducing new
                        evidence. Despite Sterling’s credentials as a statistician and his appeal
                        towards the public’s confirmation bias, he did not fool everyone. In 1972,
                        when Sterling was invited to a meeting for the American Association for the
                        Advancement of Science, his presentation entitled “Difficulties of Measuring
                        the Effects of Air Pollution vs the Effects of Smoking” was criticized by
                        members for “presenting no new data” and having “an axe to grind” with
                        epidemiologists like Hammond, charging that they did not make their data
                        freely available for review. Overall, “the paper [had] no scientific merit
                        or worth” according to one reporter. The reporter went on, saying that “the
                        refusal of the investigators [Sterling] to permit review, and in depth
                        analysis of all data, is in fact a violation of sound, accepted scientific
                        approach.”
                        <EssaySideNote
                            content="JMB. “Report on Difficulties of Measuring the Effects of Air
                            Pollution vs the Effects of Smoking - A Paper Presented to Theodor D.
                            Sterling at the 138th Meeting of the American Association for the
                            Advancement of Science. December 27 1972.” 10 January 1973."
                            url="https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=jjym0053"
                        />
                        Such a statement paints Sterling as a hypocrite, given his own attacks on
                        other researchers during his presentation. These claims and comments aren’t
                        surprising considering most of Sterling’s research was less experimental and
                        more data driven, while also critiquing any claims that might hurt the big
                        tobacco companies.
                    </p>
                    <p>
                        Sterling’s network graph offers us insights into how Sterling triangulated
                        his position between academia and industry. From the graph, we can see that
                        he was a central figure and intermediary between academics at Harvard and
                        John Hopkins to those in the industry working for the CTR or the American
                        Cancer Society. When looking deeper into Sterling’s connections with other
                        researchers beyond the CTR versus within it, it is interesting to note the
                        relationship he has with some of them. When Sterling sent a letter in 1971
                        to Dr. Cuyler Hammond in 1971 requesting access to Hammond’s data to analyze
                        his methods, he addressed Hammond very professionally and even used a lot of
                        flattery.
                        <EssaySideNote
                            content='Theodor Sterling, "Letter to E. Cuyler Hammond," March 18,
                            1971.'
                            url="https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=gsnd0137"
                        />
                        This seems appropriate considering Hammond is the same researcher
                        whose research Sterling had been paid to criticize before for drawing far
                        fetched conclusions. Hammond wrote back, declining to give his data to
                        Sterling due to privacy concerns.
                        <EssaySideNote
                            content='E. Cuyler Hammond, "Letter to Theodor Sterling," March 31,
                            1971.'
                            url="https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=kxhg0215"
                        />
                        Though we don’t know for sure, we can
                        likely assume that Hammond realized Sterling’s connection to the tobacco
                        industry (or at least remembered what Sterling said about his previous
                        research) and did not want to allow for his research to be exploited by
                        Sterling and the CTR.
                    </p>
                    <p>
                       In comparison, many letters between Sterling and his associates at the CTR
                        started formal, but over a few years, many of the letters have friendlier
                        tones and even discuss get togethers between him and his recipient. For
                        instance, this can be seen in letters between Sterling and Dr. Robert
                        Hockett of the CTR. At first, his letters are very professional and even
                        address Dr. Hockett by his full name and title,
                        <EssaySideNote
                            content='Theodor Sterling, "Letter to Robert Hockett," March 30, 1964.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=zykp0215'
                        />
                        but over the years, Sterling
                        begins addressing Hockett by his nickname and using a friendlier, less
                        professional tone, even going to the extent of discussing meeting up the
                        next time Sterling is in town.
                        <EssaySideNote
                            content='Theodor Sterling, "Letter to Robert Hockett," April 1, 1980.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=fzwb0005'
                        />
                        This progression in the tone of the letters
                        over the years, suggests a close relationship between Sterling and his
                        colleagues at the CTR in comparison to his relationship between him and
                        researchers at the American Cancer Society, such as Hammond.
                    </p>
                    <p>
                        Finally, the Sterling’s network graph helps demonstrate his connection
                        between his research and the lawyers for the tobacco industry. Their
                        connection had two main caveats: the first was that most of Sterling’s work,
                        research, and ideas were sent to lawyers such as William Shin of Shook,
                        Hardy, and Bacon to then be passed on to the big tobacco companies and the
                        second was many of Sterling’s budget requests would go to these lawyers (as
                        well as the CTR) for approval and payment. Sometimes, Sterling sent letters
                        to the lawyers of the big tobacco companies describing ways in which they
                        could attack the legitimacy of other research results, such as the Cigarette
                        Smokers Annual from 1966
                        <EssaySideNote
                            content='Theodor Sterling, "Letter to William Shinn," January 3, 1968.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=xxcj0102'
                        />
                        or Hammond’s data and the Surgeon General’s report.
                        <EssaySideNote
                            content='Theodor Sterling, "Letter to William Shinn," May 7, 1970.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=gzwd0040'
                        />
                        Another example is Sterling suggesting a strategy that the lawyers and
                        tobacco companies could use was placing an ad into a well read scientific
                        journal discussing how other researchers were keeping their data private
                        and unavailable for analysis.
                        <EssaySideNote
                            content='Theodor Sterling, "Letter to William Shinn," August 14, 1970.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=hnvw0040'
                        />
                        Another main talking point between Sterling
                        and the lawyers representing the tobacco companies was the issue of
                        financing and budgets. In many letters, Sterling asked for funds, such as
                        for travel to conferences in other countries,
                        <EssaySideNote
                            content='Theodor Sterling, "Letter to William Shinn," February 29,
                            1972.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=ylbw0040'
                        />
                        or sending them a proposed
                        budget for further research opportunities.
                        <EssaySideNote
                            content='Theodor Sterling, "Letter to William Shinn," May 7, 1970.'
                            url='https://www.industrydocuments.ucsf.edu/tobacco/docs/#id=lhgd0040'
                        />
                        Overall, Sterling’s connection
                        with the lawyers shows another way that he was an intermediary and
                        connection between industry and academia.
                    </p>
                </section>
            </>;

        //
        // const content =
        //     ;

        return(
            <MainLayout
                content={
                    <EssayView
                        title='Ted Sterling: The Man, the Myth, the Liar'
                        epigraph={epigraph}
                        introduction={introduction}
                        authors='Ife Ademolu-Odeneye, Crista Falk, and Jordan Wilke'
                        dataset_name='sterling'
                        essay_content={essay_content}
                    />
                }
            />

        )
    }
}

export default SterlingEssayView;
