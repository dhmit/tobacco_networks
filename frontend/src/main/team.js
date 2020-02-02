import React from 'react';
import MainLayout from "./main_layout";
import './team.css'

export class AboutView extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const render_team_member = (name, img_src) => {
            return (
                <div className="col-6 col-md-3 col-lg-2">
                    <div className="team-member">
                        <img className="mx-auto rounded-circle"
                            src={img_src} alt={name}/>
                        <h4>{name}</h4>
                        <p className="text-muted">UROP</p>
                    </div>
                </div>
            )};

        const render_staff = (name, img_src, position) => {
            return (
                <div className="col-sm-6 text-center">
                    <div className="team-member-lg">
                        <img className="mx-auto rounded-circle"
                            src={img_src}
                            alt={name} />
                        <h4>{name}</h4>
                        <p className="text-muted">{position}</p>
                    </div>
                </div>
            )
        };

        const render_staff_lower = (name, img_src, position) => {
            return (
                <div className="col-sm-4 text-center">
                    <div className="team-member-lg">
                        <img className="mx-auto rounded-circle"
                            src={img_src}
                            alt={name} />
                        <h4>{name}</h4>
                        <p className="text-muted">{position}</p>
                    </div>
                </div>
            )
        };

        const content = (
            <>
                <div>
                    <div className="row">
                        <div className="col-12">
                            <h1 className="display-4">About this Project</h1>

                            <p>
                                How do you sift through several decades-worth of documents from
                                the Tobacco industry to paint a cohesive picture of how its
                                major players have deceived and misled the public about the
                                dangers of smoking?
                            </p>
                            <p>
                                Led by MIT postdoctoral associate Stephan Risi, the Tobacco
                                Networks project’s goal was to produce a general network
                                visualization of roughly 11 million documents of data related to
                                Tobacco researchers, lawyers, and marketing experts in a way
                                that visually elucidates the connections between significant
                                people and corporations in the industry. In this way, links
                                which highlight the sinister and overwhelming efforts to
                                propagate pro-cigarette platforms, often backed by false
                                research put out by major institutions, could be clearly formed.
                            </p>
                            <p>
                                The anticipated scope of the Tobacco Networks project is to
                                provide a resource for those studying the strategies employed by
                                tobacco companies throughout history to persuade consumers and
                                mask the addictive effects of the drug.
                            </p>
                            <p>You can find the code for this project on <a className="about_link"
                                href="https://github.com/dhmit/tobacco_networks">Github.</a></p>
                            <p>The documents themselves are available at the UCSF’s <a
                                className="about_link"
                                href="https://www.industrydocuments.ucsf.edu/tobacco/">
                                Truth Tobacco Industry Documents Archive.
                            </a></p>
                        </div>
                    </div>
                    <section id="lab">
                        <div className="container">
                            <div className="row">
                                <div className="col-lg-12 text-center">
                                    <h1 className="display-4">Staff and
                                        Members</h1>
                                </div>
                            </div>
                            <div className="row">
                                {render_staff("Michael Scott Cuthbert",
                                    "/static/img/team/Cuthbert_Michael.jpg",
                                    "Faculty Director & Associate Professor")}

                                {render_staff("Ryaan Ahmed",
                                    "/static/img/team/Ahmed_Ryaan.jpg",
                                    "Technical Director Senior Research Engineer")}
                            </div>
                            <div className="row">
                                {render_staff_lower("Stephan Risi",
                                    "/static/img/team/Risi_Stephan.jpg",
                                    "Postdoctoral Associate")}

                                {render_staff_lower("Erica Zimmer",
                                    "/static/img/team/Zimmer_Erica.jpg",
                                    "Postdoctoral Associate")}

                                {render_staff_lower("Nicole Fountain",
                                    "/static/img/team/Fountain_Nicole.jpg",
                                    "Administrative Assistant")}
                            </div>

                            <div className="row">
                                {render_team_member("Kidist Adamu",
                                    "/static/img/team/Adamu_Kidist.jpg")}

                                {render_team_member("Ife Ademolu-Odeneye",
                                    "/static/img/team/Ademolu-Odeneye_Ife.jpg")}

                                {render_team_member("Angelica Castillejos",
                                    "/static/img/team/Castillejos_Angelica.jpg")}

                                {render_team_member('Crista Falk',
                                    "/static/img/team/Falk_Crista.jpg")}

                                {render_team_member('Raquel Garcia',
                                    "/static/img/team/Garcia_Raquel.jpg")}

                                {render_team_member('Christina Wang',
                                    "/static/img/team/Wang_Mingye.jpg")}

                                {render_team_member('Jordan Wilke',
                                    "/static/img/team/Wilke_Jordan.jpg")}

                                {render_team_member('Jessica Wu',
                                    "/static/img/team/Wu_Jessica.jpg")}

                                {render_team_member('Angel Yang',
                                    "/static/img/team/Yang_Angel.jpg")}

                                {render_team_member('Sirena Yu',
                                    "/static/img/team/Yu_Sirena.jpg")}
                            </div>
                        </div>
                    </section>
                </div>
            </>
        );


        return (
            <MainLayout content={content}
            />
        );
    }
}

export default AboutView;
