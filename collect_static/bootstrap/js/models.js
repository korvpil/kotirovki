$(function() {

    RecordType = {};
    RecordType.wall = "wall";
    RecordType.topics = "topics";
    RecordType.wallcomment = "wallcomment";
    RecordType.topiccomment = "topiccomment";

    var getValue = function(object, prop) {
        if (!(object && object[prop])) return null;
        return _.isFunction(object[prop]) ? object[prop]() : object[prop];
    };

    var urlError = function() {
        throw new Error('A "url" property or function must be specified');
    };

    RecordModel = Backbone.Model.extend({

        defaults: function() {
            return {
                text: "Текст 1",
                type: RecordType.wall
            };
        },

        initialize: function() {
//            this.urlRoot = "/api/v1/wall/";
        },

        url: function() {
            var base = getValue(this, 'urlRoot') || getValue(this.collection, 'url') || urlError();
            if (this.isNew()) return base;
            var rrr = base.split("?");
            var res = rrr[0] + (rrr[0].charAt(rrr[0].length - 1) == '/' ? '' : '/') + encodeURIComponent(this.id) + "/";
            if (rrr.length > 1) {
                res += "?" + rrr[1];
            }
            return res;
        }

    });

    TopicModel = RecordModel.extend({

        defaults: function() {
            return {
                text: "Текст 1",
                type: RecordType.topics
            };
        },

        initialize: function() {
//            this.urlRoot = "/api/v1/topic/";
        }

    });

    WallCommentModel = RecordModel.extend({

        defaults: function() {
            return {
                text: "Текст 1",
                type: RecordType.wallcomment
            };
        }

    });

    RecordList = Backbone.Collection.extend({

        model: RecordModel,
        url: '/api/1.0/wall/6/',

        comparator: function(record) {
            return -record.id;
        }

    });

    FilterModel = Backbone.Model.extend({

        defaults: function() {
            return {
                name: "Фильтр 1",
                url: "",
                recordModel: RecordModel,
                type: RecordType.wall,
                group_id:0
            }
        },

        list: RecordList,

        initialize: function() {
            this.list = new RecordList();
            this.list.group_id = this.get("group_id");
            this.list.model = this.attributes.recordModel;
            this.list.bind("reset", this.listUpdate);
            this.list.bind("change", this.listUpdate);
            this.bind("add",this.loadRecords,this);
        },

        loadRecords: function() {
            this.list.url = this.get("url");
            this.list.fetch();
//            console.log("loadRecords")
        },

        listUpdate: function(mdl) {

            var rrr = mdl.map(function(val) {
                return val.get("author_id");
            });

            rrr = _.uniq(rrr);

            for(var i in rrr) {
                if (rrr[i] < 0) {
                    socialON.appView.vkUserList.addExistingUid(rrr[i],mdl.get("name"),"");
                    rrr.splice(i);
                }
            }

            if (rrr.length > 0) {
                socialON.appView.vkUserList.addUids(mdl.group_id,rrr);
            }

        }

    });

    FilterList = Backbone.Collection.extend({

        model: FilterModel

    });

    GroupModel = Backbone.Model.extend({

        defaults: function() {
            return {
                name: "Группа 1"
            };
        },

        initialize: function() {

//            console.log("GroupModel init");
            var paramstr = "?group__id=" + this.get("id");
            var paramstr_mod = paramstr + "&moderated=0&order_by=-id";
            this.filters = new FilterList();
            var wallFilter = new FilterModel({name:"Стена",url:"/api/v1/wall/" + paramstr_mod,
                group_id:this.get("id")});
            this.filters.add(wallFilter);
            var topicsFilter = new FilterModel({name:"Обсуждения",url:"/api/v1/topic/" + paramstr_mod,
                recordModel:TopicModel,type:RecordType.topics,group_id:this.get("id")});
            this.filters.add(topicsFilter);
//            this.records.fetch();

        }

    });

    GroupList = Backbone.Collection.extend({

        model: GroupModel,
        url: '/api/v1/group/'

    });

    VKUserModel = Backbone.Model.extend({

        defaults: function() {
            return {
                id: 0,
                first_name: "",
                last_name: ""
            };
        }

    });

    VKUserList = Backbone.Collection.extend({

        model: VKUserModel,

        addUids: function(group_id, uids) {
            var obj = this;

            $.ajax({
                type: "GET",
                url: "/api/v1/vkusers/",
                data: {group__id:group_id,uids:uids.join(",")},
                success: function(data) {
                    for(var i in data) {
                        obj.add(new VKUserModel({id:data[i].uid,first_name:data[i].first_name,last_name:data[i].last_name}))
                    }
                    console.log("OOOOO " + group_id);
                },
                dataType:"json"
            });
        },

        addExistingUid: function(uid, last_name, first_name) {
            this.add(new VKUserModel({id:uid,first_name:first_name,last_name:last_name}))
        }

    })

});