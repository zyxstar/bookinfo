

view是什么？
===========

Backbone的view是反映数据模型的__外观__，也被用来监听__事件__和做出相应的__反应__。

    SearchView = Backbone.View.extend({
        initialize: function(){
            alert("Alerts suck.");
        }
    });
    // The initialize function is always called when instantiating a Backbone View.
    // Consider it the constructor of the class.
    var search_view = new SearchView;


## "el"属性
`el`属性引用DOM元素，每一个view有一个`el`属性，如果未定义，将自动产生一个空的DIV元素。

制造`el`属性是div#search_container的view

    var search_view = new SearchView({ el: $("#search_container") });

注意，当绑定了容器元素时，任何事件的触发都必须在该元素内

## 加载模板
`render()`函数用来呈现el元素的表现，
由于Backbone依赖`underscore.js`，则可以使用该库的[_.template()方法](http://documentcloud.github.com/underscore/#template)来加载与渲染

    <div id="search_container"></div>

    <script type="text/javascript">
    SearchView = Backbone.View.extend({
        initialize: function(){
            this.render();
        },
        render: function(){
            //Pass variables in using Underscore.js Template
            var variables = { search_label: "My Search" };
            // Compile the template using underscore
            var template = _.template( $("#search_template").html(), variables );
            // Load the compiled HTML into the Backbone "el"
            $(this.el).html(template);
        }
    });

    var search_view = new SearchView({ el: $("#search_container") });
    </script>

    <script type="text/template" id="search_template">
        <!-- Access template variables with <%= %> -->
        <label><%= search_label %></label>
        <input type="text" id="search_input" />
        <input type="button" id="search_button" value="Search" />
    </script>


## 监听事件
使用`events`属性去监听view，注意只能监听到`el`容器的子元素（容器元素本身的不能被监听）

    SearchView = Backbone.View.extend({
        //...
        events: {
            "click input[type=button]": "doSearch"
        },
        doSearch: function( event ){
            // Button clicked, you can access the element that was clicked with event.currentTarget
            alert( "Search for " + $("#search_input").val() );
        }
    });


model是什么？
============
在backbone中model是应用的核心，包含了__交互数据__、基于这些数据的__逻辑__[通信、验证、计算的属性、访问控制等]

    Person = Backbone.Model.extend({
        initialize: function(){
            alert("Welcome to this world");
        }
    });
    var person = new Person;

`initialize`是构造方法，当new一个实例（基于model,view,collections）时被触发

## 设置属性
当需要为某些实例设置属性时

    Person = Backbone.Model.extend({
        initialize: function(){
            alert("Welcome to this world");
        }
    });
    var person = new Person({ name: "Thomas", age: 67});
    delete person;

    // or we can set afterwards, these operations are equivelent
    var person = new Person();
    person.set({ name: "Thomas", age: 67});

在new时传入一个js对象，或使用`model.set()`

## 获取属性
使用`model.get()`可以访问到model的属性

    Person = Backbone.Model.extend({
        initialize: function(){
            alert("Welcome to this world");
        }
    });
    var person = new Person({ name: "Thomas", age: 67, children: ['Ryan']});
    var age = person.get("age"); // 67
    var name = person.get("name"); // "Thomas"
    var children = person.get("children"); // ['Ryan']

## 设置model的默认属性
使用`defaults`

    Person = Backbone.Model.extend({
        defaults: {
            name: 'Fetus',
            age: 0,
            children: []
        },
        initialize: function(){
            alert("Welcome to this world");
        }
    });
    var person = new Person({ name: "Thomas", age: 67, children: ['Ryan']});
    var age = person.get("age"); // 67
    var name = person.get("name"); // "Thomas"
    var children = person.get("children"); // ['Ryan']

## 管理model属性
model可以包含多个自定义的方法（方法也是属性），而且默认这些方法是public的

    Person = Backbone.Model.extend({
        defaults: {
            name: 'Fetus',
            age: 0,
            children: []
        },
        initialize: function(){
            alert("Welcome to this world");
        },
        adopt: function( newChildsName ){
            this.get("children").push( newChildsName );
        }
    });
    var person = new Person({ name: "Thomas", age: 67, children: ['Ryan']});
    person.adopt('John Resig');
    var children = person.get("children"); // ['Ryan', 'John Resig']

## 监听model的改变
所有属性能够被侦测到值的改变，这是backbone一个非常有用的部分，下例演示当"person"的name改变时，新的name将被alert

    Person = Backbone.Model.extend({
        defaults: {
            name: 'Fetus',
            age: 0,
            children: []
        },
        initialize: function(){
            alert("Welcome to this world");
            this.bind("change:name", function(){
                var name = this.get("name"); // 'Stewie Griffin'
                alert("Changed my name to " + name );
            });
        },
        replaceNameAttr:function( name ){
            this.set({ name: name });
        }
    });
    var person = new Person({ name: "Thomas", age: 67, children: ['Ryan']});
    person.replaceNameAttr('Stewie Griffin'); // This triggers a change and will alert()

当使用`this.bind("change",function(){})`将监听该model的所有属性，参考[bind/on方法](http://backbonejs.org/#Events-on)

## 获取、保存及删除

### 小技巧

取得当前所有属性

    var person = new Person({ name: "Thomas", age: 67, children: ['Ryan']});
    var attributes = person.toJSON(); // { name: "Thomas", age: 67, children: ['Ryan']}

也可以：

    var attributes = person.attributes;

但该方法是直接引用model的属性，修改时必须小心，推荐使用`set()`来改变

### 在set或save之前进行验证
使用`validate`来验证model，返回`string`表示抛出异常，v1.0之前在`set/save`时是默认触发，v1.0起，只有`save`默认触发，在`set`时也想触发验证，需使用`{'validate':true}`，记得先要绑定`invalid`事件

    Person = Backbone.Model.extend({
        // If you return a string from the validate function,
        // Backbone will throw an error
        validate: function( attributes ){
            if( attributes.age < 0 && attributes.name != "Dr Manhatten" ){
                return "You can't be negative years old";
            }
        },
        initialize: function(){
            this.bind("invalid", function(model, error){
                // We have received an error, log it, alert it or forget it :)
                alert( error );
            });
        }
    });

    var person = new Person;
    person.set({ name: "Mary Poppins", age: -1 }, {'validate':true});
    // Will trigger an alert outputting the error
    delete person;
    var person = new Person;
    person.set({ name: "Dr Manhatten", age: -1 }, {'validate':true});
    // God have mercy on our souls


collection是什么？
=================
collection是一个包含model的有序的集合，所以它可在以下场合中被用到：
- Model: Student, Collection: ClassStudents
- Model: Todo Item, Collection: Todo List
- Model: Animals, Collection: Zoo

一般情况下，collection中的元素属于同类型的model，但是model可以属于多个collection

    var Song = Backbone.Model.extend({
        initialize: function(){
            console.log("Music is the answer");
        }
    });
    var Album = Backbone.Collection.extend({
        model: Song
    });

## 创建一个collection
    var Song = Backbone.Model.extend({
        defaults: {
            name: "Not specified",
            artist: "Not specified"
        },
        initialize: function(){
            console.log("Music is the answer");
        }
    });
    var Album = Backbone.Collection.extend({
        model: Song
    });
    var song1 = new Song({ name: "How Bizarre", artist: "OMC" });
    var song2 = new Song({ name: "Sexual Healing", artist: "Marvin Gaye" });
    var song3 = new Song({ name: "Talk It Over In Bed", artist: "OMC" });
    var myAlbum = new Album([ song1, song2, song3]);
    console.log( myAlbum.models ); // [song1, song2, song3]






