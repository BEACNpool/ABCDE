COPY (
WITH frontier_stake(view) AS (
  VALUES
    ('stake1uxaertz49825tjhczzy3heghk3nq6jugcvdxtqzn2avgeaqr64xk3'),
    ('stake1u80fnwl4jf822fvqn9p3cum5ncl6lxph0wtdrgc08mw078ct3ysht'),
    ('stake1uy4paxdaxtnnnv48fzc4r8zvwqq25x7mnl9xf7pxhar4ehqnaycxa'),
    ('stake1u9jasamtphty6907hl43t7tfecyqe2ju5lqaw3zfgad33kcvwmlue'),
    ('stake1uy6tdplul92rfp8ewuc6vmncuq7h5rgdwdlfx7hga7faf5qruws4u'),
    ('stake1u909pyegwxe8lwxya5283jctzg6ryttfy42mefyp7639ukggy2hfz'),
    ('stake1u9ua5m029qe3z8tjkmszek0q8dj3hzmxvss8aq05qqghsygg452j2'),
    ('stake1u83sjd5pa4paymq6hled52hjggwmj5yedvdhxdxuumxj7qg4kdzh3'),
    ('stake1uxh5clcr4gjdqhlhfkyljqkfpaqxkc25yfva2cxs5t2w9pc4a8c0h'),
    ('stake1uyx7rsxu9rzlhk9hhrv2enh4rz4fp820xuf06qwqj08rekqfh6j2k'),
    ('stake1uxhpml8xs6zvmtdtf2yxylp3c87xshguxlggpa4kyks966g3lvzzh'),
    ('stake1u8jzezej70zecawsdwhdlvvphuvh9dexjd33w4t3ghh692sfl5nlj'),
    ('stake1uyzfgj0336nl0llsf5rhf4s55rgema2yt82v8k9qv85pf0gy3ce85'),
    ('stake1uyg58xvhn7pmal7k0ml8d45jnvc30dla44r5lpsfv2z5r0gr93jsa'),
    ('stake1uy6rthet2e8lcv2v4j8wnex5px5xkv2l4x3pxnzzcxswgjsuldej4'),
    ('stake1u8m3lka5kk8dw849nhey8ghn8vfykf3s2cmrfteasua0umc8qq0d0'),
    ('stake1u8qdnezzx46h3wugcvadl8h2jjhs5xxystzn7xhcj5eu2rskzvvlm'),
    ('stake1ux8fdwdrdp3x498xw5hs3jskeh9cmhgj70jj593jtnpka3suxrt5s'),
    ('stake1uyj04kvgj55lqkec8uunv0y79khe85678fznm36vpa6wels4jrvlr'),
    ('stake1uycpcww6waycm2ffdfmmc4z8nvptx9er6qn84zqysx0kklstnvw38'),
    ('stake1u9jemvvyzzdgcwd9j76sd75pqaaeugv3jarcctz3sy20z6qd06lwz'),
    ('stake1ux25zszjweuansrpyf7zyvew4atfcluze95zkzj5vhrh9ncxj957z'),
    ('stake1uxmxfuwc7ljgh5erkhg2ymmaa56996c2lumpgrcagpwrsvgve8j33'),
    ('stake1uxycfkvmn98c7zq78xck6xfjtzry3t4c6akmewr8pl0ywyssvwhaf'),
    ('stake1u9qgpwv63u0zyj3ns74q2ya7ageh3x58hrseud8f3kluemqktw7lv'),
    ('stake1u97m7n66z04xv4sfzntschjsymj9qt637srwcg9wg73xlwqkmy79z'),
    ('stake1u87e9mvczlhygffmxxc9cw5947rr9c40nv474265hdmzsec0zsf5w'),
    ('stake1u8axlhzdhuxkj6vymyqzs99cymsp67dhdr0jclgk5ys03equls526'),
    ('stake1u96leu8gr29at6gwd9cmwgfurywnme09zzn0dsfegss75zggv53wh'),
    ('stake1u9ju93dl4xn4z8tdtsx5myudz8wgxr27kjp44q2ygcg8fcg036yg8'),
    ('stake1ux260hd6sp2k2pee4uucqkmegnpe7nz5zdw2ssqegeewrzss36w5p'),
    ('stake1ux35rawuxnudfht7xj3e7rvqgwz97gzs3yltf4r6yufd9ws68g7km'),
    ('stake1uys6390r4wc90qp82g9ejkmr0nyqseyp8fjspx36qumtpvgavmtv0'),
    ('stake1uxmhmkyx30xmhy8pxcmlj6d2s9m6j3z63zdp8t54y2hwudquun3pd'),
    ('stake1u8plc2hzvue43pgrwycnep3dxc67399su3pp96k0j7janusx0ny2f'),
    ('stake1u9dshqv8jgkmethg9c0ctrxnt94adyggx0yqyc5au0tketguyfhz4'),
    ('stake1uyl3ke0lznclpzf208q9f9xx8vwxz3vz5rpdyewqe2s3gtqws202p'),
    ('stake1ux2cc6jydv3np2tcp83dm687xwle2ghuw8c5l2etm4y6n5gxwwm9x'),
    ('stake1ux6fje6cc0sws3um96a0xy88mw747hxl2nng73fevy9029cy3vky8'),
    ('stake1uyxl95purw86s2zt94q3lkt7qhke6k67grkcww4qvke03tqzx9nc6'),
    ('stake1uy4prf34yvy6ywvgmj0hanlvyjmau6juyqq9tgamyf7pprs649qc5'),
    ('stake1u9l7c8fse6qs4vjfzw5m8dau66sdarzazl0zuavyluatjnsaqt0e7'),
    ('stake1uy06zq74es7lc685ll2qvpcqrewn9wq03qvrutyuyqgverqqylrnn'),
    ('stake1uxdawqyn2yft38hwc2gpc4q0ljfxv5d73sc2ce3gu0pgs8gjz5z42'),
    ('stake1u84x4z2gdsghe7rw7qy3ul0uxc63cztdl0fus0uy42sg9espyg5ru'),
    ('stake1u8zqvyvt2vj2w34l7fe5z23vmy8ds6c06tzfgyty6tgg5gcajkwcf'),
    ('stake1u9efzs7x3ldvq3q84x48nfs6dc79pngnptc0ueqmf2rhtpge7glzk'),
    ('stake1uxsqeleeq54yaf2kme8lfuccu69zktwcm3qme38kgzmzydsz856f3'),
    ('stake1u84gnwll26gswcxux3xkk2htumawr9y3sc7lwx27w5sxkeq9j7ema'),
    ('stake1uy5q9eqwydx63cf8hgazst3zuy7jjw036d48e7kx20pcqysez7230'),
    ('stake1uyflxu9aq0aqk8slskjunru2dtjvkelm6g5qwuw4uheusdq2z68gc'),
    ('stake1u9d27j582q0834v8qx422xkcdjzvyj6prjrk70rte6z62scyhw57z'),
    ('stake1uyfr6jh3x2jr77623t5phr4w2exhn54gceztnjy5vqefkpcy5rfyt'),
    ('stake1ux3afeyqyy2q4lzmy8hsekesdl9gd44sawf0zd8k5fzw42qw93uvr'),
    ('stake1u86e89c38plgyw3m36s34p2wcuj3rtk44pawjl36e4s2c9sh5xtc7'),
    ('stake1u9m34j9djfr03tqms67fa6aygatf6gtx25fr2mh9t5zxjmqhyg8p8'),
    ('stake1u9gz5x6gtkp5gvzpq5eqlavexjdj8r64lkdl96jyml5ldsszk8027'),
    ('stake1u83fznz3wpafdgnsnprrzg9ay37f8tfuz889g27ds3umkls5h8yj3'),
    ('stake1u92cg7lw8rxhzamh04xzcf3w8zsvqq7kutrwd0dz8amswlg8jjtwq'),
    ('stake1u9r83rn6y7psj5kmxs2gjpuynkrq04g8vy9zg6602m09slqzq93zl'),
    ('stake1u9rrjq00566ekuqfmhfgwtyj2qkehhxe86my0x53k4vhrescncg3r'),
    ('stake1uyruj74ku5hfqs3el2prld7e6ksstrhhh5663xrcfdnzfws5yvlhd')
),
frontier_addr(address) AS (
  VALUES
    ('addr1v98pnns6yw8zja9uxzufddpm8tsk5swxf7vv5j4vqjlswgczd4d2t'),
    ('addr1wxtwkls63ae00apdncn4hlxt6jala8367weqam9srlmul5g78wtm4'),
    ('addr1wyc9fpugnw6dprx2kly87mwk0razrh6347qmkn74glq2rlqzsmd6w'),
    ('addr1wxxaleu8a0feusutn3ntnqfg3a55hp0t5l2hqjeau0wg7cc4262zv'),
    ('addr1wymztkhaekt7derv6ceu2xhkcw4zl92m68xyvmcpqlxy0kqggmn4s'),
    ('addr1wyh9nq6fjw72mqud6w7yfe0h4tv04fxdfgcz9akczxgey8c649vxx'),
    ('addr1w9t3xx2jwwh3px0x9gcyz0cxhx29f4rcp0yrpj50ur26regz3gpyl'),
    ('addr1wx5gn92erwwd639twe3m46g3z6c9mdjdpkhcqduzq8g3xgqhwvjwu'),
    ('addr1wxwfdgvamxp0ea4sgvngnnj9pd7aa455uc8z7w54sp8ehxsp77mfy'),
    ('addr1v8aak8psnwz72gvhaawupj5fgl4ukvxz55d3jqt743z8n2sc8zwyh'),
    ('addr1wx4fknf39dsf2s4z6dkm57rmegawyjx6zpl93mju3ml8phgvsa6y8'),
    ('addr1wy4mdmkdggu369d9karndccwgx0cuyuwr7vzpdjktyh0pqsjy7j56'),
    ('addr1wx886xj2uyppjgsxxdjgzknfmykjjerfapgfyvedaagvmmgtevrtr'),
    ('addr1w9zwa7kpxxnnsndrlh5fxuydk48pax3m985q73ja4ntqgpshrvztq'),
    ('addr1w9lkk0dgvcx4d0l5uqsfd393lxdu697epugwefrjxm62dms27y90l'),
    ('addr1vyt8aeq20rvwm2wwx8yvf7kxgejhg7nmlyd032caxn3cpcc6reqkf'),
    ('addr1w8rpse9h098yhydxwwkvzlgxzgpzqc2705jjrlp2yfvcmrcpyych5'),
    ('addr1w8563gqg6yc59y3ex5wsd268nvqz8j2q59dn4nzsgumlw4s3ee8q5'),
    ('addr1w999l4d7rtccm4nutl4xam3kpw8hd4h2r7pf5u8033undccsxyfc9'),
    ('addr1w8fzzf8d7yu4mndpuy2qug57674v29l92jxmjed6vxk5y8c6qrgga'),
    ('addr1w99ezaay5hfklnwe0utel6tm7dr8dr8dq36d2xk8nkwcavqufrdlz'),
    ('addr1w9jpx6743ss3vtutj5yvsncqsavrjjw28djkfaznh2wff3c3u9ger'),
    ('addr1w9lrfu6egwy9rsygmmesr7vv247je2090k0xt2gwv5mfakqa2yzpt'),
    ('addr1w8ngjkcqjnqnljtyn7ggmw5dv66xnvu3ky6wtmk45xgducq3l087l'),
    ('addr1wyx2ezzkr2fntsztw9vj23z50xncfacrjc9n0f856r5q5fsm2h6an'),
    ('addr1w9cke0pgdfdqyqyleqdscpqx2jct6y2ah5jzpeen96n9k8q3aa3jy'),
    ('addr1w9yxkgh8y0gk7kfep3e22qxlwp77p6luzvmlghcunp0jp5cf2cmt2'),
    ('addr1wy4ehpxhdu6fgtmlhvsgayl3hl9vyn6e6433utpnyxsz35q5r6gt3'),
    ('addr1w8l3r7v6mm2tc8lmwf5m08pyxpdv7c84adnzwcrq3a6wywgnhxawa'),
    ('addr1w8p7yyzahk20zg3a380ata92tqrrrz46tnq79aymcvk3eucvdyrw9'),
    ('addr1wx83jzgct6uxk6q7cjgy4mwgp7awx0s28suwhvhf6s6jv3shk55hg'),
    ('addr1wymxsz0a2pcdels6awrmuje2czeklvutd2sgf5vqrkhd8ycjzldw2'),
    ('addr1wyzlswequusu8x0jxpyjyfj64c75trj3nxfdc0jxlm0s98cek0ujz'),
    ('addr1w8rh2jz956gyljfsddnkmxxn39frva2r2mqqhlr4gy5eltq5ggc5p'),
    ('addr1wx87jxt2mygxe8w4lmez6s0tq63v4phe4sfzjjgsg3ev3pgj6vgsy'),
    ('addr1wya04ly3vx8nk3ck2g83xddak7lv6d3wrkg4zjr5xsdh76ct46mdg'),
    ('addr1w9gcuzw480l4zmpje46euhku949wrdch0tqjddtxs32eq6ghvded0'),
    ('addr1wxm3l90j6c9mgmsl448m6c32aj7cla39a2tp2m6uk2pk5ysyqxujq'),
    ('addr1w844lrss2chvakjnpv7lggsr8xyu0j546fthgann6yv48schxssed'),
    ('addr1wxhmsfc6wuc9apnu7medcpfq7zmym336g0y9edlapt3mlgs6xcmyh'),
    ('addr1wyzn43amtgnm0narlh2xs9uuxzl0pakhn2mnmjrcmwfqkkqmrelwx'),
    ('addr1w90h8xtwgdunl82xw8rfjjp5wl7jjhk9hwrlgajwmm2e3sggh5ygh'),
    ('addr1wy6lg0epnn4hdlcjuxr9vq6wt7lg7h6yxy8fuqhy78tycxgh86epw'),
    ('addr1w8r0p249dyf5hu9qrfwdz5serqvy4mlp2mrlkg00avusthgp90v35'),
    ('addr1w8pc9aylkru96ufpyty6c0mn8xy0v924dg597dlk6u2u0cqafvwse'),
    ('addr1wyydkxjmy43slsqkdu2wldpq753qvv98kmw25e2zcqpy0xcxrgwgy'),
    ('addr1w9fru8rjgec2dg76epu2f745eagjftxp7ww8u2vx4ag9wcg0xelg7'),
    ('addr1w9japqnkp7kp0hy3t02ghhll80p4gcs5030gst953w9n4vsk2wkx3'),
    ('addr1wx8ug3y5h6vgemd7shdazzxs9tu8saauhvfvdzr400sgttg39z6re'),
    ('addr1w8udnp3jmxqjqelk8znvm5h3kms9j324a076pr2cczeealg5mxv5q'),
    ('addr1wym3nzrj0pwgnuu5umjygn732k4q0ptdz8pvlwmc6m362fcsp4xxh'),
    ('addr1w9ydexfcyjmtgltn832ydadzncacajxqsnp2g200ztmpu3qmvpw20'),
    ('addr1wyf3u26u7m8lxpmuyxxzv54vphkx5hrdpydceg6c3wqqk2s6edupw'),
    ('addr1w8jtej40lg0yz0ls7jmn3u7a8lmqhgfdzettenqnd2tmufqxt25ap'),
    ('addr1wx6hxtqq9mpflruthpckmsjl2m3zn3fcaq5xzqjy300mvycxuxq28'),
    ('addr1wx25en4gpf9rlkl9z90d4hjac4fy2pvy95kde8559756l5s389xmv'),
    ('addr1w8etm396ha867euf4tgq5qhqa3kdpxkhdpgakn709e56sxgq4yud0'),
    ('addr1wykl4vfvtkr6kv873clvadj09j0c7hgn08hfyw0y7wgkh5gp62gt9'),
    ('addr1w89jlpm9fv6fq884q9ltuc7g45yng5e54qkyk9qz5a2hxqsczev99'),
    ('addr1wxz2qprekvnv9nmg2masswqe5ynyas8tshpjahavj0q7pmgr6pfl7'),
    ('addr1wxfp2gw927kuv8a6h35naa8z397haqz4jh35wmja6dlkzmcry0727'),
    ('addr1wyd7sm5rw039qge9pvqvmrqjmzpgpv5zcmdevfc7qlvlzuc5vhppc'),
    ('addr1wxtjs8wj8tr3urkyrv4mzgjumy6paj5hzfar7kvfvz5mt7qut2hec'),
    ('addr1w8vtgr4ul4y5p8mjc84xjvn6ygvc7gul20xkl0aaxjcr4lgdxq2nm'),
    ('addr1w9cr4qxa48pg0y2cpn28fe7482h02fxl59steh55mruktyq9t7aed'),
    ('addr1w8pdylqspmc4hxqkrfpnzuzcu3rkdj9njtspe95t4cc2enggkmmgw'),
    ('addr1wx084tp8qn69z4ckgznt70ge0kmkytfc4y087c0jzmrspmq40rfkj'),
    ('addr1wy7kquw2a04m08jazydj57s70audhwzz8syrtzfe7ptemcqze7hst'),
    ('addr1wyunmsgkkyjkaay90vdc9j0vjn3az5vx9x4hlapvc3nk5gsprm2vw'),
    ('addr1wyhm7u3nmjcxevmkhlmxs2kyzvpprw538dfxm0rtt5mw8sc5mv4yv'),
    ('addr1w80fd6h60qan29zzdejrvsh6nqlq3jyaxtxrakj4fcum4jsq6sy2h'),
    ('addr1wy9fztaehywadnzv70m7jqt7t68ufrn0hpe9v2x7ljmwswc9yp0hr'),
    ('addr1wy5jwu3655nkn4ghe7v2wvqhwt6gpnqshh9ad2yd86qk50g965kwk'),
    ('addr1w9u7ww8n5rta5xjggz8ra67wu7r0nnvgzkaxggyul2m8xgsx277yl'),
    ('addr1w8n4pmwexa6wtsy7n9e7mc4dlpjlaku8xx53xduwkg2shkcvwhg2a'),
    ('addr1w9dhjd8z3ceevv0mw992scz76u4a4glgtv02nps3amjjvuc29sypv'),
    ('addr1w9n0nsmye3f8hr0h9euzwxhq3vtcv63f9vkyxnv63gwl0ksrnxhme'),
    ('addr1wxe268va0qd5jzxmvtlt9rgnrwzr82h3u8n63mmpn3mgj4gdaqj5g'),
    ('addr1wyzqm98x7wrgtcy3wtrg4uvjgpysw4nqcsxgneattzcpp7qmyc9sg'),
    ('addr1w8g3n0xzngd0slg9d0lv4jsu8xttadvj0wkg9e09slmzefgunzj46'),
    ('addr1wxygjyrpvw9l7gkj64dtsdg0rp2pjs0hh4vg9l7eat3tlvgrx0j2s'),
    ('addr1wyfn3jwru4shmzfrf035szlskzyhth30us8zu7s78rhjs5qw3700u'),
    ('addr1wyhjzyfn0hyhtfgq6n2u65c0apd6naud9lrn8p7yqsshsjcky9frl'),
    ('addr1w86yf0gy2w5lhn4l7xfrpu3rpsz2avsxrhdz77rkm4al07s62swg2'),
    ('addr1wx9sfvff2q23kr23hda7vl3xcpjffrwuptpjme2hgurux6snhmlzs'),
    ('addr1w8xe54mtmtthnyu7rv3ee93sglv0u6lrmf660msnnkrdy4sttc3qx'),
    ('addr1w9h0n7d8cxn4qjz6zcrfxu5ve75qyact74pl0gz999swmdsm8w678'),
    ('addr1wxrnm2l2jyyp9stht3vdfuyqgg4am67k9xu4vafufnersyglj8wmh'),
    ('addr1wykfx37ut49rm2hqfkg0e6msmnm3g342ke3yzerd2jh5ukcljpa2m'),
    ('addr1wy4jvq7e4n9aw9n4xlkfshksmpq25f4nsuamk5jv5gfjcvcu35vma'),
    ('addr1w95ap9plunjyw0ly20vg55emd77yynsyw6d8xchp6wqt0pcrr2ntz'),
    ('addr1wyl29mcyk998j2c4tah6fq5jqq5w8kq7nss284rmucrxr4gmm8acg'),
    ('addr1w9ucvqdx3a6txz44f3pw32whqn0jw63nm9jelm4ae8fptyc0enr6c'),
    ('addr1wylz559hq9khw9hn7sqg5rl8g0jcg6d9jsqnrzpanefyh0s2glggg'),
    ('addr1w989dk8syavsszshrecdar5jc4wxhpeahm7c9jrtnfyxgkc93m799'),
    ('addr1wy7rzfzqzwhhwel2j8mqlcsam22ytvqv4z796js5lxxd04g5rsg9y'),
    ('addr1wym866j8wu7032pupgxvdvfdkrnnrtsxlsf0g7aps2zq22szwjrqw'),
    ('addr1w9qn4w9jj7app443re5lkzun8cc6m9c78vkjdl9z05mqzwgxc3cxj'),
    ('addr1w8pkxp9f07dcywfdfr7eeegd4cwe6n3grejl68q783rm9eqrshs0l'),
    ('addr1vywm8egs68x5kns0t4qj7vttm7mut05grs2wmwlmqljahegphndwc'),
    ('addr1wxusgxnh798vxqc08y09xhwesgtpdwch0908xqf40ydlqrg8pd35c'),
    ('addr1wxclr3e3qkukduux6slxvhky86gjh256xjrncg5arf8krage8c24y'),
    ('addr1w99ehfx4dzkt98ep8tvd4gfflwk08fn22j3yk35hxpmn0usqq5d09'),
    ('addr1w9yyes7tnat5cmfdweuz9hqnl50e90dhuw2artnrsw0wnecqhd5zm'),
    ('addr1w8hn4pgf9hnnl9waceyy8h0v0juk9p4jy6yjg9787xwsymgh0hptl'),
    ('addr1wytxv8u2lpf97hrkcnfuxyapl58nfp0tascvms0zgg2q2ksdjzmhu'),
    ('addr1w8tl9jyp4cp7tpwxvrsmanpkphzaysm8h8v7r6p468ngv4q5g4zg0'),
    ('addr1w8rv0h094fffv054tgsccu9lfjf46zeuwryle6lxk05kuhg4jsxsc'),
    ('addr1wx99l5vuf4f9pltur0njlchujdfpv8a4q9zq69wmah5augqeklha5'),
    ('addr1w8a4au84jnmres4x87enc0d05fyrykhf3hpc066kj30h0xq9yrt5u'),
    ('addr1w8f54klegmh5xkcwgl94p49dczwhp0lqqrc67pssadsf36g6czcr8'),
    ('addr1w8p8l8dn7lfpzz9fptvmkckcty5eapttq5szdzmglvauutsel8xlc'),
    ('addr1w9n6mn90rweg2va2nde9f2m6tst439zj8k45vqkpgnde25qvxjsmj'),
    ('addr1w8gyhzcj2fglymea95tgpvqvgp44sqwclcqv45wpwrrduzc9dp9gt'),
    ('addr1w9s52c6u75wk3ywrycx5lff7fvnrm4cfr3c0nvgrj8kl7mcgv4xt6'),
    ('addr1w829tvklhux7jasppd6afgyd5el00dtz7g2dnjk5crw3ayczaawph'),
    ('addr1w9y5suzdgdjwyvtdcdkup9kfnvjgywuvt22te6py5fucnqq0rflv6'),
    ('addr1wxezw85aff33u5c2j7umg67yy7t0ap4aexauwz578vrdhtq7yugxm'),
    ('addr1wxn80nzmnpkz0vftmvqa8ppl6465r44myu7wqtll3xe047g9v733r'),
    ('addr1w9z75htxma7aeqkj8ddgrxqfqmck9xptrahd2s6g47hykmcmn3e99'),
    ('addr1wyezym9ky2h070755glzxjsr489kh5gsutalnj5asu34rhqan7glm'),
    ('addr1w8dd7306e8ttfpsrdvgd32pcp6fqztxsw3v8psrhwpreqkqj53vtw'),
    ('addr1wxnvhtpp5lmnxseehwjhfsc5ez56ydpjcmjce67jkkxlsss3lf66g'),
    ('addr1w9cf6w0zz2h7jmmy3mgj6t5vacg5xyfrca0fuvlue2ey2fq38edk6'),
    ('addr1w85q2zzwtkkq3ka0ge7x75kyl3rca2v9gfcfxd0dlr3exaqdewtr3'),
    ('addr1wypsntw3wec4zrsydv4wccx39735qzvm7qa4mp2qn6zsxmg2nty9j'),
    ('addr1w8sca2hl8y475uemnulx9azz0ld2k8axrup3xmasectef2g3x4hcd'),
    ('addr1wy6laan8ahxc0mes73crdd0y80k7kuxkyr4grl4e2j7m48qketv89'),
    ('addr1w8axhvewzxc4f9erlq5y0mmjlp29kh5c3d9r59tmy7c685gfpmupj'),
    ('addr1wx3avrf0ykfjd2s0vt57cx4zvavsdzs6g2wrn8t33yfuzpqvmhdjg'),
    ('addr1w90cykc9q7khz88dj9na08rwxfrghlsjfyvftesr7p5xnys57fl58'),
    ('addr1wxymgc76vu2cr4l6tn6q8kthju59fzzzjwze5k5uq8w27lgvqn79v'),
    ('addr1wx6qljt7y93g5ja9jhts9r9tau9a3k5u5f42j8uvvtryeycfwng4a'),
    ('addr1w8y9pz8ucensehmc4e39ys2a9lsmh6pvcc75ax4dpk3ew3qqefuvj'),
    ('addr1wyc62n5pv9e07xxdkwyg5jqrn6qdfd5k3fqqk3qjm0y3sts0nlmnh'),
    ('addr1wxmfmn9vzal24vazmn374wyvhp0hxjem98e9ecsz6dw8ptc8236cx'),
    ('addr1wy9gvuhf2njcemhtut4keg2sd0mpny6d8330ft4jar86gpqsl8f4q'),
    ('addr1w9twqu4zqwgentkufleptuzef25c839hmnkjsjqwutsn9kg4zwg4z'),
    ('addr1w8ypm7a6pe6rlsaq4ksc75lvdh50hzwz5hedsqnr0h952lqkq8elz')
),
seed_utxos AS (
  SELECT DISTINCT
    txo.tx_id,
    txo.index AS tx_index,
    txo.value,
    CASE
      WHEN sa.view IN (SELECT view FROM frontier_stake) THEN 'stake'
      WHEN txo.address IN (SELECT address FROM frontier_addr) THEN 'enterprise'
      ELSE NULL
    END AS frontier_kind
  FROM tx_out txo
  LEFT JOIN stake_address sa ON sa.id = txo.stake_address_id
  WHERE sa.view IN (SELECT view FROM frontier_stake)
     OR txo.address IN (SELECT address FROM frontier_addr)
),
spend_txs AS (
  SELECT DISTINCT
    ti.tx_out_id AS spend_tx_id,
    su.value AS src_value,
    su.frontier_kind
  FROM seed_utxos su
  JOIN tx_in ti ON ti.tx_in_id = su.tx_id AND ti.tx_out_index = su.tx_index
),
spend_summary AS (
  SELECT spend_tx_id,
         COUNT(*) AS frontier_input_count,
         SUM(src_value) AS frontier_input_lovelace,
         COUNT(*) FILTER (WHERE frontier_kind = 'stake') AS stake_input_count,
         COUNT(*) FILTER (WHERE frontier_kind = 'enterprise') AS enterprise_input_count
  FROM spend_txs
  GROUP BY spend_tx_id
),
dest_rows AS (
  SELECT
    ss.spend_tx_id,
    encode(t.hash,'hex') AS spend_tx_hash,
    b.epoch_no,
    b.time AS block_time,
    ss.frontier_input_count,
    ss.frontier_input_lovelace,
    ss.stake_input_count,
    ss.enterprise_input_count,
    txo.index AS dest_index,
    txo.address AS dest_address,
    txo.value AS dest_lovelace,
    sa.view AS dest_stake_address,
    CASE
      WHEN sa.view IN (SELECT view FROM frontier_stake) THEN 'internal_stake'
      WHEN txo.address IN (SELECT address FROM frontier_addr) THEN 'internal_address'
      WHEN sa.view IS NOT NULL THEN 'external_stake'
      ELSE 'enterprise'
    END AS dest_type
  FROM spend_summary ss
  JOIN tx t ON t.id = ss.spend_tx_id
  JOIN block b ON b.id = t.block_id
  JOIN tx_out txo ON txo.tx_id = ss.spend_tx_id
  LEFT JOIN stake_address sa ON sa.id = txo.stake_address_id
),
shape AS (
  SELECT spend_tx_id,
         COUNT(*) AS total_output_count,
         COUNT(*) FILTER (WHERE dest_type LIKE 'internal%') AS internal_output_count,
         COUNT(*) FILTER (WHERE dest_type = 'external_stake') AS external_stake_output_count,
         COUNT(*) FILTER (WHERE dest_type = 'enterprise') AS enterprise_output_count,
         COALESCE(SUM(dest_lovelace) FILTER (WHERE dest_type LIKE 'internal%'), 0) AS internal_output_lovelace,
         COALESCE(SUM(dest_lovelace) FILTER (WHERE dest_type = 'external_stake'), 0) AS external_stake_output_lovelace,
         COALESCE(SUM(dest_lovelace) FILTER (WHERE dest_type = 'enterprise'), 0) AS enterprise_output_lovelace
  FROM dest_rows
  GROUP BY spend_tx_id
),
latest_pool AS (
  SELECT DISTINCT ON (d.addr_id)
    d.addr_id,
    d.pool_hash_id,
    d.active_epoch_no,
    d.slot_no,
    d.tx_id,
    d.cert_index
  FROM delegation d
  JOIN stake_address sa ON sa.id = d.addr_id
  WHERE sa.view IN (
    SELECT DISTINCT dest_stake_address FROM dest_rows WHERE dest_stake_address IS NOT NULL
  )
  ORDER BY d.addr_id, d.active_epoch_no DESC, d.slot_no DESC, d.tx_id DESC, d.cert_index DESC
),
latest_vote AS (
  SELECT DISTINCT ON (dv.addr_id)
    dv.addr_id,
    dv.drep_hash_id,
    tx.block_id,
    dv.tx_id,
    dv.cert_index
  FROM delegation_vote dv
  JOIN tx ON tx.id = dv.tx_id
  JOIN stake_address sa ON sa.id = dv.addr_id
  WHERE sa.view IN (
    SELECT DISTINCT dest_stake_address FROM dest_rows WHERE dest_stake_address IS NOT NULL
  )
  ORDER BY dv.addr_id, tx.block_id DESC, dv.tx_id DESC, dv.cert_index DESC
)
SELECT
  dr.spend_tx_hash,
  dr.epoch_no,
  dr.block_time,
  dr.frontier_input_count,
  dr.frontier_input_lovelace,
  dr.stake_input_count,
  dr.enterprise_input_count,
  dr.dest_index,
  dr.dest_type,
  dr.dest_address,
  dr.dest_stake_address,
  dr.dest_lovelace,
  sh.total_output_count,
  sh.internal_output_count,
  sh.external_stake_output_count,
  sh.enterprise_output_count,
  sh.internal_output_lovelace,
  sh.external_stake_output_lovelace,
  sh.enterprise_output_lovelace,
  ph.view AS current_pool,
  dh.view AS current_drep
FROM dest_rows dr
JOIN shape sh ON sh.spend_tx_id = dr.spend_tx_id
LEFT JOIN stake_address sa ON sa.view = dr.dest_stake_address
LEFT JOIN latest_pool lp ON lp.addr_id = sa.id
LEFT JOIN pool_hash ph ON ph.id = lp.pool_hash_id
LEFT JOIN latest_vote lv ON lv.addr_id = sa.id
LEFT JOIN drep_hash dh ON dh.id = lv.drep_hash_id
WHERE dr.dest_type NOT LIKE 'internal%'
  AND dr.dest_lovelace >= 49000000000
ORDER BY dr.dest_lovelace DESC, dr.spend_tx_hash, dr.dest_index
) TO STDOUT WITH CSV HEADER;
