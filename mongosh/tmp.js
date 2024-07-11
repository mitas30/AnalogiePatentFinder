// パイプライン定義
//DBの選択は自分でやろうね
const pipeline = [
    {
        $lookup: {
            from: "patents",
            localField: "original_id",
            foreignField: "_id",
            as: "patent_docs"
        }
    },
    {
        $match: {
            patent_docs: { $size: 0 }
        }
    },
    {
        $project: {
            _id: 1
        }
    }
];

// パイプライン実行と結果表示
const idsToDelete=db.abstracts.aggregate(pipeline).toArray().map(doc => doc._id);

if (idsToDelete.length > 0) {
    const deleteResult = db.abstracts.deleteMany({ _id: { $in: idsToDelete } });
    print(`Deleted ${deleteResult.deletedCount} documents.`);
} else {
    print("No documents to delete.");
}
    
