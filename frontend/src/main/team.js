import React from 'react';
import MainLayout from "./main_layout";
//import MainLayout from "./main_layout";

export class TeamView extends React.Component {
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
                    <div className="team-member team-member-lg">
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
                    <div className="team-member team-member-lg">
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
                            <h1>About this Project</h1>
                            <p>Crista description:</p> {//TODO remove this line after
                            // checking the description
                            }
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
                        </div>
                    </div>
                    <section id="lab">
                        <div className="container">
                            <div className="row">
                                <div className="col-lg-12 text-center">
                                    <h1 className="section-subheading text-muted">Staff and
                                        Members</h1>
                                </div>
                            </div>
                            <div className="row">
                                {render_staff("Michael Scott Cuthbert",
                                    "img/team/Cuthbert_Michael.jpg",
                                    "Faculty Director & Associate Professor")}

                                {render_staff("Ryaan Ahmed",
                                    "img/team/Ahmed_Ryaan.jpg",
                                    "Technical Director Senior Research Engineer")}
                            </div>
                            <div className="row">
                                {render_staff_lower("Stephan Risi",
                                    "img/team/Risi_Stephan.jpg",
                                    "Postdoctoral Associate")}

                                {render_staff_lower("Erica Zimmer",
                                    "img/team/Zimmer_Erica.jpg",
                                    "Postdoctoral Associate")}

                                {render_staff_lower("Nicole Fountain",
                                    "img/team/Fountain_Nicole.jpg",
                                    "Administrative Assistant")}
                            </div>

                            <div className="row">
                                {render_team_member("Kidist Adamu",
                                    "img/team/Adamu_Kidist.jpg")}

                                {render_team_member("Ife Ademolu-Odeneye",
                                    "img/team/Ademolu-Odeneye_Ife.jpg")}

                                {render_team_member("Angelica Castillejos",
                                    "img/team/Castillejos_Angelica.jpg")}

                                {render_team_member('Crista Falk',
                                    "img/team/Falk_Crista.jpg")}

                                {render_team_member('Raquel Garcia',
                                    "img/team/Garcia_Raquel.jpg")}

                                {render_team_member('Christina Wang',
                                    "img/team/Wang_Mingye.jpg")}

                                {render_team_member('Jordan Wilke',
                                    "img/team/Wilke_Jordan.jpg")}

                                {render_team_member('Jessica Wu',
                                    "img/team/Wu_Jessica.jpg")}

                                {render_team_member('Funing Yang',
                                    "img/team/Yang_Funing.jpg")}
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

export default TeamView;
