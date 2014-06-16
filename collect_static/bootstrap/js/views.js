$(function() {

    _.templateSettings = {
        interpolate : /\{\{(.+?)\}\}/g
    };

    var ElemView = Backbone.View.extend({

        commTemplate:_.template('<button class="btn btn-tiny commbtn" role="button">нк: {{ count }}</button>\
        '),

        template:_.template('<div class="btn-group group-left" data-toggle="buttons-checkbox">\
        <button class="btn btn-tiny"><i class="icon-flag"></i></button>\
        </div>\
    <div class="btn-group group-right">\
        <button class="btn btn-tiny btn-success"><i class="icon-ok icon-white"></i></button>\
        <button class="btn btn-tiny btn-danger"><i class="icon-remove icon-white"></i></button>\
        <button class="btn btn-tiny btn-warning"><i class="icon-trash icon-white"></i></button>\
    </div>\
    <div class="btn-group group-bottom">\
        {{ commBtn }}\
        </div>\
    <b>{{ username }}</b>\
        <div>{{ text }}</div>'),
//        <button class="btn btn-tiny" data-target="#moreModal" role="button" data-toggle="modal">подробнее</button>\

        className: "elem",
        model: RecordModel,
        parentModel: null,

        events: {
            "click .btn-danger": "deleteClick",
            "click .btn-success": "moderatedClick",
            "click .commbtn": "commentsClick"
        },

        initialize: function() {
            this.model.bind('change', this.render, this);
//            socialON.appView.vkUserList.bind("reset", this.render, this);
            socialON.appView.vkUserList.bind("all", this.render, this);
/*            if (this.model.get("type") != RecordType.topics) {
                this.model.bind('change', this.renderTopic, this);
            }else{
                this.model.bind('change', this.render, this);
            }*/
//            this.model.bind('destroy', this.remove, this);
        },

        render: function() {
            var comms = this.model.get("comments_new");
            var commBtnStr = "";
            if (comms > 0) {
                commBtnStr = this.commTemplate({count:comms});
            }

            var author = socialON.appView.vkUserList.get(this.model.get("author_id"));
            console.log(this.model.get("author_id"));
            console.log(author);
            var authorName = "";
//            var authorName = author.get("last_name") + " " + author.get("first_name");

            if (this.model.get("type") == RecordType.topics) {
                this.$el.html(this.template({text:this.model.get("title"),username:"Вася Пупкин " + authorName +  this.model.get("id"),
                    commBtn: commBtnStr}));
            }else{
                this.$el.html(this.template({text:this.model.get("text"),username:"Вася Пупкин " + authorName + this.model.get("id"),
                    commBtn: commBtnStr}));
            }

            if (this.model.get("moderated") == 1) {
                this.$el.find(".group-right button,.group-left button").attr("disabled","disabled");
            }

            return this;
        },

        deleteClick: function() {
            var view = this;
            console.log("deleteClick " + this.model.id);
            console.log("deleteClick " + this.model.url());
            this.model.destroy({
                success:function() {
                    if (view.parentModel) {
                        view.parentModel.set("comments_new",view.parentModel.get("comments_new")-1);
                    }
                    view.remove();
                }
            });
        },

        moderatedClick: function() {
            var view = this;
            console.log("moderatedClick " + this.model.id);
            this.model.save("moderated",1,{
                success:function() {
                    if (view.parentModel) {
                        view.parentModel.set("comments_new",view.parentModel.get("comments_new")-1);
                    }
                    view.remove();
                }
            });
        },

        commentsClick: function() {

            var parentRecord = this.model;

            var comList = new RecordList();
            if (parentRecord.get("type") == RecordType.topics) {
                var paramstr = "?topic__id=" + this.model.get("id");
                var paramstr_mod = paramstr + "&moderated=0&order_by=-id";

                comList.url = "/api/v1/topiccomment/" + paramstr_mod;
            }else{
                paramstr = "?record__id=" + this.model.get("id");
                paramstr_mod = paramstr + "&moderated=0&order_by=-id";

                comList.url = "/api/v1/wallcomment/" + paramstr_mod;
            }
            comList.fetch({
                success: function() {
                    window.socialON.appView.commentsView.showDialog(comList,parentRecord);
                }
            });

        }

    });

    var FilterView = Backbone.View.extend({

        template:_.template('<div class="head">\
            {{ title }} <a href="#" class="add">Добавить</a>\
            </div>\
            <div class="content"></div>'),

        className: "column",
        model: null,

        events: {
            "click .head .add": "addMessage"
        },

        initialize: function() {
            this.model.bind('change', this.render, this);
            this.model.list.on("reset", this.listReset, this);
            this.model.list.on("all", this.listReset, this);
        },

        render: function() {
            this.$el.html(this.template({title:this.model.get("name"),addlink:this.model.get("url")}));
            return this;
        },

        listReset: function() {
            var ctx = this;

            var $cont = this.$el.find(".content");
            $cont.empty();

            this.model.list.each(function(record) {
                if (record.get("moderated") == 0 || record.get("comments_new") != 0) {
                    var elemView = new ElemView({model:record});
                    $cont.append(elemView.render().el);
                }
            });
        },

        addMessage: function(e) {
            e.preventDefault();
            switch(this.model.get("type")) {
                case RecordType.wall:
                    window.socialON.appView.addWallMessageView.showDialog(this.model.list);
                    break;
                case RecordType.topics:
                    window.socialON.appView.addTopicView.showDialog(this.model.list);
                    break;
            }
        }

    });

    var AddWallMessageView = Backbone.View.extend({
        el : "#addMessageModal",
        model: RecordList,

        events: {
            "click .btn-primary": "addClick"
        },

        showDialog: function(model) {
            this.model = model;
            this.$el.modal('show');
        },

        addClick: function(e) {
            e.preventDefault();

            var mdl = new RecordModel({text:this.$el.find("textarea[name='newMessage']").val()});
            this.model.create(mdl,{wait: true});
        }
    });

    var AddTopicView = Backbone.View.extend({
        el : "#addTopicModal",
        model: RecordList,

        events: {
            "click .btn-primary": "addClick"
        },

        showDialog: function(model) {
            this.model = model;
            this.$el.modal('show');
        },

        addClick: function(e) {
            e.preventDefault();

            var mdl = new TopicModel({
                text:this.$el.find("textarea[name='text']").val(),
                title:this.$el.find("input[name='title']").val()
            });
            this.model.create(mdl,{wait: true});
        }
    });

    var AddWallCommentView = Backbone.View.extend({
        el : "#addWallCommentModal",
        model: RecordList,

        events: {
            "click .btn-primary": "addClick"
        },

        showDialog: function(model) {
            this.model = model;
            this.$el.modal('show');
        },

        addClick: function(e) {
            e.preventDefault();

            var mdl = new WallCommentModel({text:this.$el.find("textarea[name='newComment']").val()});
            this.model.create(mdl,{wait: true});
        }
    });

    var CommentsView = Backbone.View.extend({
        el : "#commentsModal",
        model: RecordModel,
        parentModel: RecordModel,

        events: {
            "click .addBtn": "addClick"
        },

        showDialog: function(model,parentModel) {
            this.model = model;
            this.parentModel = parentModel;
            this.render();
            this.$el.modal('show');
        },

        addClick: function(e) {
            e.preventDefault();

            window.socialON.appView.addWallCommentView.showDialog(this.model);
        },

        initialize: function() {
            this.model.bind('change', this.render, this);
        },

        render: function() {
            var ctx = this;

            var $cont = this.$el.find(".modal-body");
            $cont.empty();

            this.model.each(function(record) {
                console.log(record);
/*                var mdl = new WallCommentModel({id:record.id,text:record.text});
                mdl.urlRoot = "/api/v1/wallcomment/";*/
//                if (record.get("moderated") == 0) {
                    var elemView = new ElemView({model:record});
                    elemView.parentModel = ctx.parentModel;
                    $cont.append(elemView.render().el);
//                }
            });
        }

    });

    var AppView = Backbone.View.extend({

        el: $(".workspace"),
        $tabsBar: $(".content-box .nav-tabs"),
        $tabsContent: $(".content-box .tab-content"),

        tabTemplate:_.template('<li><a href="#group{{ id }}" data-toggle="tab">{{ name }}</a></li>'),
        tabContTemplate:_.template('<div id="group{{ id }}" class="columns tab-pane"></div>'),

        events: {
            "click #MyTextButton": "renderTabs"
        },

        bone : null,

        initialize: function() {

/*            this.bone = new TastyBone.Bone('/api/v1/');
            var view = this;

            this.bone.on('ready', function get_collections() {
                console.log("HEELLL!");
//                console.log(view.bone.collections.GroupCollection());

                view.groupList = new view.bone.collections.GroupCollection();
                view.groupList.bind('reset', view.groupReset, view);
                view.groupList.fetch();

            });*/

            this.groupList = new GroupList();
//            this.groupList.bind('all', this.renderTabs, this);
            this.groupList.bind('reset', this.groupReset, this);
            this.groupList.fetch();

            this.vkUserList = new VKUserList();

            this.addWallMessageView = new AddWallMessageView();
            this.addTopicView = new AddTopicView();
            this.commentsView = new CommentsView();
            this.addWallCommentView = new AddWallCommentView();
        },

        userListReset: function() {

            console.log("rwerwerwerwe");

        },

        groupReset: function() {
            var ctx = this;

            this.$tabsBar.empty();
            this.$tabsContent.empty();

            this.groupList.each(function (group) {
                ctx.$tabsBar.append(ctx.tabTemplate(group.attributes));
                ctx.$tabsContent.append(ctx.tabContTemplate(group.attributes));

                var $groupCont = $("#group"+group.get("id"));

                group.filters.each(function (filter) {
                    var filterView = new FilterView({model:filter});
                    $groupCont.append(filterView.render().el);
                });
            });

            this.$tabsBar.find("li:first").addClass("active");
            this.$tabsContent.find("div:first").addClass("active");

/*            this.groupList.each(function (group) {
                var wallFilter = group.filters.where({name:"Стена"})[0];
                console.log(wallFilter);
//                .bind('all', ctx.renderElems, group);
//                group.records.fetch();
            });*/
        },

        renderTabs: function() {

/*            for(var i = 0;i < this.groupList.length;i++) {
                console.log("zzz = ", this.groupList.get(i));
            }*/



/*            var zzz = "";
            var zzzCont = "";

            this.groupList.each(function (group) {
                zzz += this.tabTemplate(group.attributes);

                var elems = "";
                console.log("id ", group.id);
                console.log(group.records);
//                group.records.each(function (record) {
//                    console.log("zzzz");
//                    elems += this.elemTemplate({username:"Вася Пупкин",text:record.text});
//                });

                var col = this.columnTemplate({title:"Стена",content:elems});

                zzzCont += this.tabContTemplate({id:group.get("id"),content:col});
            }, this);

            this.$tabsBar.html(zzz);
            this.$tabsContent.html(zzzCont);

            this.$tabsBar.find("li:first").addClass("active");
            this.$tabsContent.find("div:first").addClass("active");*/

        },

        v_obj:this,

        renderElems : function() {
            console.log("renderElems", this);
            var elems = "";
            var group_id = this.id;
            this.records.each(function (record) {
                var elem = new ElemView({model:record});
                $("#group"+group_id+" .content").append(elem.render().el);
            });
//            $("#group"+this.id+" .content").html(elems);
        },

        groupAdd: function() {
            var ctx = this;
            this.groupList.each(function (group) {
                var wallFilter = group.filters.where({name:"Стена"})[0];
                console.log(wallFilter);
//                .bind('all', ctx.renderElems, group);
//                group.records.fetch();
            });
        }

    });

    var SocialON = function() {

        var obj = {};

//        obj.groupList = new GroupList;
        obj.appView = new AppView;

        return obj;
    };

    window.socialON = new SocialON();
/*    window.socialON.appView.groupList.add(new GroupModel());*/

});